import { group } from 'k6';
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '200s', target: 200 },
    { duration: '20s', target: 100 },
    { duration: '10s', target: 0 },
  ],
};

export function setup() {
  let payload = {
    username: "admin@mail.ru",
    password: "admin",
  };

  const response = http.post("http://127.0.0.1/login", payload);
  check(response, { 'status was 200': (r) => r.status === 200 });
  const token = response.json().access_token;
  return { token };
}

export default function (data) {
  const token = data.token;

  group('user', function () {
    login();
    get_user(token);
    create_order(token);
    get_orders(token);
  });

  sleep(3);
}

function login() {
  let payload = {
    username: "admin@mail.ru",
    password: "admin",
  };

  const response = http.post("http://127.0.0.1/login", payload);
  check(response, { 'status was 200': (r) => r.status === 200 });
  sleep(3)
}

function get_user(token) {
  const response = http.get("http://127.0.0.1/me", { headers: { 'Authorization': `Bearer ${token}` } });
  check(response, { 'status was 200': (r) => r.status === 200 });
  sleep(3);
}

function create_order(token) {
  const orderForm = [
    {
      menu_position_id: 2,
      count: 2
    },
    {
      menu_position_id: 5,
      count: 3
    }
  ];
  const response = http.post("http://127.0.0.1/order", JSON.stringify(orderForm),
      { headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` } });
  check(response, { 'status was 200': (r) => r.status === 200 });
  sleep(3);
}

function get_orders(token) {
  const response = http.get("http://127.0.0.1/orders", { headers: { 'Authorization': `Bearer ${token}` } });
  check(response, { 'status was 200': (r) => r.status === 200 });
  sleep(3);
}