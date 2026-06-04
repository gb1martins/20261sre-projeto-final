import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 }, // ramp-up to 20 users
    { duration: '1m', target: 20 },  // stay at 20 users
    { duration: '30s', target: 0 },  // ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'], // 95% of requests must be below 3s
    http_req_failed: ['rate<0.01'],    // error rate must be less than 1%
  },
};

export default function () {
  const res = http.get('http://host.docker.internal:8501');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
