import { registerOTel } from "@vercel/otel";

export function register() {
  registerOTel({
    serviceName: "bec_pydantic_ai-frontend",
  });
}