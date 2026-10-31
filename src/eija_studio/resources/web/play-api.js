// How PlayIDE reads its local server's answers. A stopped server, a crash page or a proxy error page becomes an Error
// with a stable code and a sentence a person can act on, never a bare "Failed to fetch" or a JSON parse message.
// Messages end without a full stop, like the server's own, because callers add their own sentence after them.
// A JSON answer, refusals included, passes through exactly as before: `code` and `message` are the server's own.
"use strict";
const PlayApi = (() => {
  const failure = (code, message, status) => Object.assign(new Error(message), { code, status });

  async function read(response) {
    let value, parsed = true;
    try { value = await response.json(); } catch { parsed = false; }
    if (!parsed) {
      throw failure("RESPONSE_INVALID", `The local server answered HTTP ${response.status} without a readable result; `
        + "the terminal running eija serve says what went wrong", response.status);
    }
    if (!response.ok) throw failure(value && value.code, (value && value.message) || "Request failed", response.status);
    return value;
  }

  async function request(fetchImpl, path, options) {
    let response;
    try { response = await fetchImpl(path, options); } catch {
      throw failure("SERVER_UNREACHABLE", "PlayIDE cannot reach its local server; check that eija serve is still running", 0);
    }
    return read(response);
  }

  return Object.freeze({ read, request });
})();
if (typeof module !== "undefined") module.exports = PlayApi;
