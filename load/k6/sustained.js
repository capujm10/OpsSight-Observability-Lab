import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 10,
  duration: "5m",
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<1200"],
  },
};

const baseUrl = __ENV.BASE_URL || "http://api:8000";

export default function () {
  const res = http.get(`${baseUrl}/api/v1/orders`, {
    headers: { "x-correlation-id": `k6-sustained-${__VU}-${__ITER}` },
  });
  check(res, {
    "orders endpoint is successful": (r) => r.status === 200,
  });
  sleep(0.5);
}
