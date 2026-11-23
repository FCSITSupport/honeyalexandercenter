// Honey Alexander Center: serves the GitHub Pages site
// (github.com/FCSITSupport/honeyalexandercenter) at honeyalexandercenter.org.
// Deployed as the Cloudflare Worker "honeywebsite", with custom domains
// honeyalexandercenter.org and www.honeyalexandercenter.org.
const ORIGIN = "https://fcsitsupport.github.io/honeyalexandercenter";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405, headers: { Allow: "GET, HEAD" } });
    }
    let path = url.pathname;
    if (path === "/" || path === "/index.html") path = "/";
    else if (path === "/og.jpg") path = "/assets/honey-alexander-center.jpg";
    else if (!path.startsWith("/assets/")) return Response.redirect(url.origin + "/", 301);

    const upstream = await fetch(ORIGIN + path, {
      method: request.method,
      cf: { cacheEverything: true, cacheTtl: 300 },
    });
    if (!upstream.ok) {
      return new Response("Not found", { status: upstream.status === 404 ? 404 : 502 });
    }
    const headers = new Headers(upstream.headers);
    headers.set("cache-control", path === "/" ? "public, max-age=300" : "public, max-age=86400");
    headers.set("x-content-type-options", "nosniff");
    headers.set("referrer-policy", "strict-origin-when-cross-origin");
    headers.delete("x-github-request-id");
    headers.delete("via");
    return new Response(upstream.body, { status: upstream.status, headers });
  },
};
