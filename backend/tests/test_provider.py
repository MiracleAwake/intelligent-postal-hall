import unittest

from app.capabilities.skills import fill_known_fields, materials_for_intent, precheck_materials, understand_request
from app.provider.client import CircuitOpen, ModelCallError, Provider, parse_intent_reply
from app.provider.profiles import load_profiles


class ProviderTrial(unittest.TestCase):
    def test_profiles_keep_keys_out_of_file(self):
        profiles = load_profiles()
        self.assertEqual(profiles["hall_local"].model, "deepseek-r1:1.5b")
        self.assertEqual(profiles["hall_cloud"].api_key_env, "GLM_API_KEY")
        text = profiles["hall_cloud"].__repr__()
        self.assertNotIn("sk-", text)

    def test_strips_think_and_reads_intent(self):
        parsed = parse_intent_reply('<think>先想</think>\n{"intent":"改存期","summary":"一年改三年"}')
        self.assertEqual(parsed["intent"], "改存期")
        self.assertTrue(parsed["parsed"])

    def test_breaker_opens_without_network(self):
        def boom(url, body, timeout, headers):
            raise TimeoutError("down")

        provider = Provider(transport=boom)
        provider.breakers["hall_local"].limit = 2
        with self.assertRaises(ModelCallError):
            provider.complete("hi", profile_id="hall_local")
        with self.assertRaises(ModelCallError):
            provider.complete("hi", profile_id="hall_local")
        with self.assertRaises(CircuitOpen):
            provider.complete("hi", profile_id="hall_local")

    def test_fake_model_returns_intent(self):
        def ok(url, body, timeout, headers):
            self.assertIn("/api/chat", url)
            return {"message": {"content": '{"intent":"取息","summary":"利息转活期"}'}}

        provider = Provider(transport=ok)
        result = provider.recognize_intent({"intent": "想把利息取出来", "amount": "20000.00"})
        self.assertEqual(result["executor"], "model")
        self.assertEqual(result["intent"], "取息")
        self.assertEqual(result["profile_id"], "hall_local")

    def test_skills_keep_missing_fields(self):
        def ok(url, body, timeout, headers):
            prompt = body["messages"][0]["content"]
            if "应带" in prompt:
                content = '{"missing":["身份证"],"ready":false}'
            elif "已知" in prompt:
                content = '{"fields":{"amount":"20000.00"},"missing":["new_term"]}'
            else:
                content = '{"forms":["定期存款凭条"],"summary":"改存期"}'
            return {"message": {"content": content}}

        provider = Provider(transport=ok)
        forms = materials_for_intent(provider, "改存期")
        filled = fill_known_fields(provider, {"amount": "20000.00"})
        checked = precheck_materials(provider, ["身份证", "存单"], ["存单"])
        self.assertEqual(forms["forms"], ["定期存款凭条"])
        self.assertEqual(filled["fields"], {"amount": "20000.00"})
        self.assertEqual(filled["missing"], ["customer_ref", "old_term", "new_term"])
        self.assertIn("身份证", checked["missing"])
        self.assertFalse(checked["ready"])

    def test_understand_request_drops_unknown_intent(self):
        def ok(url, body, timeout, headers):
            return {"message": {"content": '{"intents":["改存期","乱写"],"interest":"连本带息","new_term":"三年","base_amount":null,"add_amount":"50000.00","print_new_certificate":true,"party":"本人","missing":[],"summary":"连息加钱"}'}}

        provider = Provider(transport=ok)
        result = understand_request(provider, "连息转三年再加五万", profile_id="hall_local")
        self.assertEqual(result["intents"], ["改存期"])
        self.assertEqual(result["new_term"], "3年")
        self.assertEqual(result["add_amount"], "50000")
        self.assertNotIn("乱写", result["intents"])
