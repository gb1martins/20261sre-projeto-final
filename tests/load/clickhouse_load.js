import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 }, // ramp-up to 50 users
    { duration: '1m', target: 50 },  // stay at 50 users
    { duration: '30s', target: 0 },  // ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of database queries should be < 500ms
  },
};

export default function () {
  const url = 'http://host.docker.internal:8123/';
  const payload = 'SELECT * FROM gold_order_metrics LIMIT 100';
  const params = {
    headers: {
      'Content-Type': 'text/plain',
      'X-ClickHouse-User': 'northwind',
      'X-ClickHouse-Key': 'northwind',
    },
  };

  const res = http.post(url, payload, params);
  check(res, {
    'status is 200': (r) => r.status === 200,
    'body has data': (r) => r.body.length > 0,
  });
  sleep(0.5);
}
