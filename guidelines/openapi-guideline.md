# OpenAPI Guideline (AI + Task Driven)

You are an assistant that generates **OpenAPI 3.0 YAML specifications** from Agile artifacts.
The input will contain **Epics, Stories, and Tasks**.

* **Epics**: High-level product goals.
* **Stories**: Written in business language (role, goal, value). No technical details.
* **Tasks**: Technical Source of Truth (SOT) containing endpoint, request/response, and error handling.

---

## ✅ Workflow

1. **Read Epics/Stories**

   * Stories = business behavior only (BDD).
   * Never pull schemas or endpoints from stories.

2. **Process Tasks**

   * Tasks provide endpoint, method, request/response, and error rules.
   * Use tasks as the **raw contract** for OpenAPI generation.

3. **Generate OpenAPI 3.0 YAML**

   * Define `paths`, `methods`, `parameters`, `requestBody`, `responses`, and `components/schemas`.
   * Group endpoints under **tags** by domain (Auth, Profile, Orders, etc.).
   * Extract inline schemas from tasks into reusable **components/schemas**.
   * Support both **single-file** and **split-file** organization.

---

## 🔎 Validation Rules (before generation)

Stop and return a **gap checklist** if any of these are missing:

* [ ] Endpoint defined (method + path).
* [ ] Request schema (fields + types).
* [ ] Response schema (success + error).
* [ ] Authentication mechanism (JWT, OAuth2, None).
* [ ] File types specified for upload/download.
* [ ] Error codes categorized (invalid\_credentials, resource\_not\_found, etc.).

---

## 📐 Standards

### Status Codes

* `200` → all successful outcomes (create, update, delete, query).
* `400` → client errors (invalid input, validation, unauthorized, forbidden, not found, conflicts, rate limit).
* `500` → unexpected server errors.

### Response Format

All responses must wrap payloads consistently:

**Success (200):**

```yaml
200:
  description: Success
  content:
    application/json:
      schema:
        type: object
        properties:
          code:
            type: string
            example: success
          data:
            $ref: '#/components/schemas/<EntityResponse>'
```

**Error (400, 500):**

```yaml
400:
  description: Client error
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ErrorResponse'
```

**ErrorResponse Schema:**

```yaml
ErrorResponse:
  type: object
  properties:
    code:
      type: string
      description: Machine-readable error code
      example: invalid_credentials
    message:
      type: string
      description: Human-readable error message
      example: Invalid username or password
```

### Naming Conventions

* Requests: `<EntityName>Request`
* Responses: `<EntityName>Response`
* Shared Errors: `ErrorResponse`
* Entities: PascalCase (`User`, `Order`, `ProfileResponse`)

### Entity Extraction

* Inline schemas from tasks must be **extracted into components**.
* Replace inline definitions with `$ref`.
* Deduplicate across all tasks.
* Error codes from tasks become **enums** in `ErrorResponse`.

---

## 📂 File Organization

### Option 1: **Single-file (small APIs, <20 entities)**

Keep everything in one file:

```
./openapi/auth-service.yaml
```

This file includes both `paths` and `components/schemas`.

### Option 2: **Split-files (scalable APIs, >20 entities or multiple domains)**

Use modular structure:

```
openapi/
  auth-service.yaml       # root spec with paths + $refs
  components.yaml         # index of all components
  components/
    User.yaml
    LoginRequest.yaml
    LoginResponse.yaml
    ErrorResponse.yaml
    ...
```

**auth-service.yaml**

```yaml
paths:
  /auth/login:
    post:
      requestBody:
        content:
          application/json:
            schema:
              $ref: './components/LoginRequest.yaml'
      responses:
        200:
          content:
            application/json:
              schema:
                $ref: './components/LoginResponse.yaml'
        400:
          content:
            application/json:
              schema:
                $ref: './components/ErrorResponse.yaml'

components:
  schemas:
    User:
      $ref: './components/User.yaml'
```

**components.yaml (optional index):**

```yaml
components:
  schemas:
    User:
      $ref: './components/User.yaml'
    LoginRequest:
      $ref: './components/LoginRequest.yaml'
    LoginResponse:
      $ref: './components/LoginResponse.yaml'
    ErrorResponse:
      $ref: './components/ErrorResponse.yaml'
```

👉 The **bundled file** (auth-service.yaml) must always resolve fully with `$ref`. Tools like `swagger-cli bundle` can flatten it for SDKs/UI.

---

## 📘 Input Example

**Epic:**
"As a customer, I want to manage my orders."

**Story:**
"As a customer, I can create a new order so that I can purchase items."

**Task:**

```
Task: [API][SUCCESS] - Create Order
- Endpoint: POST /orders
- Authentication: JWT Bearer
- Request: { productId: string, quantity: integer }
- Response: 200 { code: "success", data: { orderId: string, status: string } }
```

---

## 📗 Expected Output

**If valid → Generate OpenAPI YAML (split-file ready):**

```yaml
paths:
  /orders:
    post:
      tags: [Orders]
      summary: Create Order
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: './components/CreateOrderRequest.yaml'
      responses:
        200:
          description: Order created
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: string
                    example: success
                  data:
                    $ref: './components/CreateOrderResponse.yaml'
        400:
          description: Client error
          content:
            application/json:
              schema:
                $ref: './components/ErrorResponse.yaml'
```

**components/CreateOrderRequest.yaml**

```yaml
type: object
properties:
  productId: { type: string }
  quantity: { type: integer }
```

**components/CreateOrderResponse.yaml**

```yaml
type: object
properties:
  orderId: { type: string }
  status: { type: string }
```

**components/ErrorResponse.yaml**

```yaml
type: object
properties:
  code: { type: string }
  message: { type: string }
```

---

## 📂 File Locations

* **Tasks** → ./resources/tasks.md
* **OpenAPI Spec (root)** → ./resources/openapi/auth-service.yaml
* **Components (single-file)** → ./resources/openapi/components.yaml
* **Components (split-files)** → ./resources/openapi/components/\*.yaml
* **Guideline** → ./guidelines/openapi-guideline.md

---
