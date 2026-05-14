import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 2,
  duration: "1m",
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<1000"],
  },
};

const baseUrl = __ENV.BASE_URL || "http://api:8000";

export default function () {
  const res = http.get(`${baseUrl}/api/v1/orders`, {
    headers: { "x-correlation-id": `k6-smoke-${__VU}-${__ITER}` },
  });
  check(res, {
    "orders endpoint is successful": (r) => r.status === 200,
  });
  sleep(1);
}
