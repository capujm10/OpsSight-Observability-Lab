import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "30s", target: 5 },
    { duration: "1m", target: 40 },
    { duration: "30s", target: 5 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.10"],
    http_req_duration: ["p(95)<1500"],
  },
};

const baseUrl = __ENV.BASE_URL || "http://api:8000";

export default function () {
  const chooseFailure = Math.random() < 0.05;
  const path = chooseFailure ? "/api/v1/simulate/dependency-failure" : "/api/v1/orders";
  const res = http.get(`${baseUrl}${path}`, {
    headers: { "x-correlation-id": `k6-spike-${__VU}-${__ITER}` },
  });
  check(res, {
    "expected status class": (r) => [200, 503].includes(r.status),
  });
  sleep(0.2);
}
