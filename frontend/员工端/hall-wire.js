/* 挚邮员工端的接入。壳上的按键把请求交到这里。
   没有转写就不要编一句。文件只换 file_id，字节不留在页面上。
   跨岗只提交转交。口令不经过这里。 */
(function () {
  function post(url, body) {
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {})
    }).then(function (res) { return res.json(); });
  }

  window.HallWire = {
    speech: function (body) { return post("/api/speech", body); },
    upload: function (file) {
      var data = new FormData();
      data.append("file", file, file.name);
      return fetch("/api/files", { method: "POST", body: data }).then(function (res) { return res.json(); });
    },
    handoff: function (body) { return post("/api/handoff", body); },
    inbox: function (owner) {
      return fetch("/api/handoff?to_owner=" + encodeURIComponent(owner || "")).then(function (res) {
        return res.json();
      });
    },
    act: function (body) { return post("/api/act", body); },
    session: function (body) {
      return post("/api/session", {
        no: body && body.no,
        post: body && body.post,
        role: body && body.role,
        site: body && body.site
      });
    }
  };
})();
