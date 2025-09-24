Task: [API][SUCCESS] - User Login
// GIVEN a registered user with valid credentials
// WHEN POST /auth/login
// THEN 200 with JWT response

**API Specification:**
- Endpoint: POST /v1/auth/login
- Authentication: None
- Request: { username: string, password: string }
- Response: 200 { code: "success", data: { access_token: string, token_type: string, expires_in: number, user: { id: string, email: string, fullname: string } } }

**Acceptance Criteria:**
- Accepts username or email as identifier
- Issues signed JWT with expiration
- Response excludes sensitive fields

---

Task: [API][FAIL][REQUEST] - Login Request Errors
// GIVEN missing or malformed request data
// WHEN POST /v1/auth/login
// THEN 400 with validation error response

**API Specification:**
- Endpoint: POST /v1/auth/login
- Authentication: None
- Request: { identifier: string, password: string }
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- 400 for missing required fields (identifier, password)
- 400 for malformed JSON or invalid data types

---

Task: [API][FAIL][CREDENTIALS] - Login Credential Errors
// GIVEN incorrect credentials
// WHEN POST /v1/auth/login
// THEN 400 with authentication error response

**API Specification:**
- Endpoint: POST /v1/auth/login
- Authentication: None
- Request: { username: string, password: string }
- Response: 400 { code: "invalid_credentials" | "unauthorized_access", message: string }

**Acceptance Criteria:**
- 400 for wrong username/password combination
- Generic message prevents user enumeration

---

Task: [API][FAIL][ACCOUNT] - Login Account State Errors
// GIVEN user account with restricted state
// WHEN POST /v1/auth/login
// THEN 400 with account state error response

**API Specification:**
- Endpoint: POST /v1/auth/login
- Authentication: None
- Request: { username: string, password: string }
- Response: 400 { code: "account_disabled" | "account_expired" | "account_protected", message: string }

**Acceptance Criteria:**
- 400 for disabled accounts
- 400 for expired accounts
- 400 for protected accounts (security measures)

---

Task: [API][SUCCESS] - User Logout
// GIVEN an authenticated user
// WHEN POST /auth/logout
// THEN 200 and token invalidated

**API Specification:**
- Endpoint: POST /auth/logout
- Authentication: JWT Bearer
- Request: {}
- Response: 200 { code: "success", data: {} }

**Acceptance Criteria:**
- Token becomes invalid for future requests
- Idempotent operation

---

Task: [API][FAIL][REQUEST] - Logout Request Errors
// GIVEN missing or invalid authentication
// WHEN POST /auth/logout
// THEN 400 with error response

**API Specification:**
- Endpoint: POST /auth/logout
- Authentication: JWT Bearer
- Request: {}
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- No side effects on server state

---

Task: [API][SUCCESS] - Get User Profile
// GIVEN an authenticated user
// WHEN GET /auth/profile
// THEN 200 with ProfileResponse

**API Specification:**
- Endpoint: GET /auth/profile
- Authentication: JWT Bearer
- Request: {}
- Response: 200 { code: "success", data: { id: string, email: string, firstName: string, lastName: string, createdAt: string, updatedAt: string } }

**Acceptance Criteria:**
- Returns current user's profile data
- Excludes sensitive information

---

Task: [API][FAIL][REQUEST] - Profile Request Errors
// GIVEN missing or invalid authentication
// WHEN GET /auth/profile
// THEN 400 with error response

**API Specification:**
- Endpoint: GET /auth/profile
- Authentication: JWT Bearer
- Request: {}
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- No data leakage

---

Task: [API][SUCCESS] - Admin List Users
// GIVEN an admin user
// WHEN GET /auth/profiles with optional filters
// THEN 200 with paginated users list

**API Specification:**
- Endpoint: GET /auth/profiles
- Authentication: Admin Required
- Request: { page?: number, page_size?: number, ordering?: string, email?: string }
- Response: 200 { code: "success", data: { users: array, total: number, page: number, page_size: number } }

**Acceptance Criteria:**
- Supports pagination and filtering
- Requires admin permission
- Response excludes sensitive fields

---

Task: [API][FAIL][CREDENTIALS] - Admin Access Denied
// GIVEN a non-admin user
// WHEN GET /auth/profiles
// THEN 400 with error response

**API Specification:**
- Endpoint: GET /auth/profiles
- Authentication: JWT Bearer
- Request: {}
- Response: 400 { code: "unauthorized_access", message: string }

**Acceptance Criteria:**
- No disclosure of other users' existence

---

Task: [API][SUCCESS] - Update Profile
// GIVEN an authenticated user
// WHEN PUT /auth/profile with valid fields
// THEN 200 with updated profile

**API Specification:**
- Endpoint: PUT /auth/profile
- Authentication: JWT Bearer
- Request: { firstName?: string, lastName?: string, email?: string }
- Response: 200 { code: "success", data: { id: string, email: string, firstName: string, lastName: string, updatedAt: string } }

**Acceptance Criteria:**
- Editable fields: firstName, lastName, email
- Restricted fields: id, roles, permissions cannot be modified

---

Task: [API][FAIL][REQUEST] - Profile Update Request Errors
// GIVEN malformed request data
// WHEN PUT /auth/profile
// THEN 400 with validation errors

**API Specification:**
- Endpoint: PUT /auth/profile
- Authentication: JWT Bearer
- Request: { firstName?: string, lastName?: string, email?: string }
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- 400 for malformed JSON or invalid field types

---

Task: [API][FAIL][PROFILE] - Profile Update Data Errors
// GIVEN conflicting or invalid profile data
// WHEN PUT /auth/profile
// THEN 400 with data conflict errors

**API Specification:**
- Endpoint: PUT /auth/profile
- Authentication: JWT Bearer
- Request: { firstName?: string, lastName?: string, email?: string }
- Response: 400 { code: "duplicate_resource", message: string }

**Acceptance Criteria:**
- 400 for email already in use by another user

---

Task: [API][SUCCESS] - Request Password Reset
// GIVEN an email address
// WHEN POST /auth/password-reset
// THEN 200 and reset email sent

**API Specification:**
- Endpoint: POST /auth/password-reset
- Authentication: None
- Request: { email: string }
- Response: 200 { code: "success", data: {} }

**Acceptance Criteria:**
- Always returns 200 to prevent email enumeration
- Sends reset email if account exists

---

Task: [API][FAIL][REQUEST] - Password Reset Request Errors
// GIVEN missing or invalid email format
// WHEN POST /auth/password-reset
// THEN 400 with validation errors

**API Specification:**
- Endpoint: POST /auth/password-reset
- Authentication: None
- Request: { email: string }
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- 400 for missing email field
- 400 for invalid email format

---

Task: [API][SUCCESS] - Confirm Password Reset
// GIVEN a valid reset token and new password
// WHEN POST /auth/password-reset/confirm
// THEN 200 and password updated

**API Specification:**
- Endpoint: POST /auth/password-reset/confirm
- Authentication: None
- Request: { token: string, password: string }
- Response: 200 { code: "success", data: {} }

**Acceptance Criteria:**
- Token validated (signature and expiration)
- Password policy enforced

---

Task: [API][FAIL][REQUEST] - Password Reset Confirm Request Errors
// GIVEN missing or malformed request data
// WHEN POST /auth/password-reset/confirm
// THEN 400 with validation errors

**API Specification:**
- Endpoint: POST /auth/password-reset/confirm
- Authentication: None
- Request: { token: string, password: string }
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- 400 for missing required fields
- 400 for weak password

---

Task: [API][FAIL][CREDENTIALS] - Password Reset Token Errors
// GIVEN invalid or expired token
// WHEN POST /auth/password-reset/confirm
// THEN 400 with token errors

**API Specification:**
- Endpoint: POST /auth/password-reset/confirm
- Authentication: None
- Request: { token: string, password: string }
- Response: 400 { code: "invalid_credentials" | "unauthorized_access", message: string }

**Acceptance Criteria:**
- 400 for malformed/expired/used tokens

---

Task: [API][SUCCESS] - Change Password
// GIVEN an authenticated user
// WHEN POST /auth/change-password
// THEN 200 and password updated

**API Specification:**
- Endpoint: POST /auth/change-password
- Authentication: JWT Bearer
- Request: { current_password: string, new_password: string }
- Response: 200 { code: "success", data: {} }

**Acceptance Criteria:**
- Verify current password
- Enforce password policy

---

Task: [API][FAIL][REQUEST] - Change Password Request Errors
// GIVEN missing or malformed request data
// WHEN POST /auth/change-password
// THEN 400 with validation errors

**API Specification:**
- Endpoint: POST /auth/change-password
- Authentication: JWT Bearer
- Request: { current_password: string, new_password: string }
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- 400 for missing required fields
- 400 for weak new password

---

Task: [API][FAIL][CREDENTIALS] - Change Password Credential Errors
// GIVEN wrong current password
// WHEN POST /auth/change-password
// THEN 400 with credential errors

**API Specification:**
- Endpoint: POST /auth/change-password
- Authentication: JWT Bearer
- Request: { current_password: string, new_password: string }
- Response: 400 { code: "invalid_credentials", message: string }

**Acceptance Criteria:**
- 400 for incorrect current password

---

Task: [API][SUCCESS] - Get My Roles
// GIVEN an authenticated user
// WHEN GET /auth/user/roles
// THEN 200 with assigned roles

**API Specification:**
- Endpoint: GET /auth/user/roles
- Authentication: JWT Bearer
- Request: {}
- Response: 200 { code: "success", data: { roles: array } }

**Acceptance Criteria:**
- Returns directly assigned roles

---

Task: [API][SUCCESS] - Get My Permissions
// GIVEN an authenticated user
// WHEN GET /auth/user/permissions
// THEN 200 with effective permissions

**API Specification:**
- Endpoint: GET /auth/user/permissions
- Authentication: JWT Bearer
- Request: {}
- Response: 200 { code: "success", data: { permissions: array } }

**Acceptance Criteria:**
- Consolidates permissions via roles and direct grants

---

Task: [API][FAIL][CREDENTIALS] - User Roles/Permissions Access Denied
// GIVEN missing/invalid token
// WHEN GET /auth/user/roles or /auth/user/permissions
// THEN 400 with error response

**API Specification:**
- Endpoint: GET /auth/user/roles, GET /auth/user/permissions
- Authentication: JWT Bearer
- Request: {}
- Response: 400 { code: "unauthorized_access", message: string }

**Acceptance Criteria:**
- No partial data returned

---

Task: [API][SUCCESS] - Manage Roles (CRUD)
// GIVEN an admin user
// WHEN using /auth/roles endpoints
// THEN 200 responses for CRUD operations

**API Specification:**
- Endpoint: GET /auth/roles, POST /auth/roles, GET /auth/roles/{id}, PUT /auth/roles/{id}, DELETE /auth/roles/{id}
- Authentication: Admin Required
- Request: varies by operation
- Response: 200 { code: "success", data: { role: object } } or { code: "success", data: { roles: array } }

**Acceptance Criteria:**
- Unique role name validation
- Pagination for list operations

---

Task: [API][FAIL][REQUEST] - Role Management Request Errors
// GIVEN malformed request data
// WHEN modifying roles
// THEN 400 with validation errors

**API Specification:**
- Endpoint: POST /auth/roles, PUT /auth/roles/{id}
- Authentication: Admin Required
- Request: varies by operation
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- 400 for missing required fields or invalid data

---

Task: [API][FAIL][CREDENTIALS] - Role Management Access Errors
// GIVEN non-admin user
// WHEN accessing role management endpoints
// THEN 400 with access denied

**API Specification:**
- Endpoint: GET /auth/roles, POST /auth/roles, PUT /auth/roles/{id}, DELETE /auth/roles/{id}
- Authentication: JWT Bearer
- Request: varies by operation
- Response: 400 { code: "unauthorized_access", message: string }

**Acceptance Criteria:**
- 400 for non-admin access attempts

---

Task: [API][FAIL][PROFILE] - Role Management Data Errors
// GIVEN invalid role data or constraints
// WHEN modifying roles
// THEN 400 with data conflict errors

**API Specification:**
- Endpoint: POST /auth/roles, PUT /auth/roles/{id}, DELETE /auth/roles/{id}
- Authentication: Admin Required
- Request: varies by operation
- Response: 400 { code: "duplicate_resource" | "resource_not_found" | "resource_in_use", message: string }

**Acceptance Criteria:**
- 400 for duplicate role names
- 400 for role not found
- 400 for role-in-use conflicts

---

Task: [API][SUCCESS] - Manage Permissions (CRUD)
// GIVEN an admin user
// WHEN using /auth/permissions endpoints
// THEN 200 responses for CRUD operations

**API Specification:**
- Endpoint: GET /auth/permissions, POST /auth/permissions, GET /auth/permissions/{id}, PUT /auth/permissions/{id}, DELETE /auth/permissions/{id}
- Authentication: Admin Required
- Request: varies by operation
- Response: 200 { code: "success", data: { permission: object } } or { code: "success", data: { permissions: array } }

**Acceptance Criteria:**
- Unique permission validation
- Pagination for list operations

---

Task: [API][FAIL][REQUEST] - Permission Management Request Errors
// GIVEN malformed request data
// WHEN modifying permissions
// THEN 400 with validation errors

**API Specification:**
- Endpoint: POST /auth/permissions, PUT /auth/permissions/{id}
- Authentication: Admin Required
- Request: varies by operation
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- 400 for missing required fields or invalid data

---

Task: [API][FAIL][CREDENTIALS] - Permission Management Access Errors
// GIVEN non-admin user
// WHEN accessing permission management endpoints
// THEN 400 with access denied

**API Specification:**
- Endpoint: GET /auth/permissions, POST /auth/permissions, PUT /auth/permissions/{id}, DELETE /auth/permissions/{id}
- Authentication: JWT Bearer
- Request: varies by operation
- Response: 400 { code: "unauthorized_access", message: string }

**Acceptance Criteria:**
- 400 for non-admin access attempts

---

Task: [API][FAIL][PROFILE] - Permission Management Data Errors
// GIVEN invalid permission data or constraints
// WHEN modifying permissions
// THEN 400 with data conflict errors

**API Specification:**
- Endpoint: POST /auth/permissions, PUT /auth/permissions/{id}, DELETE /auth/permissions/{id}
- Authentication: Admin Required
- Request: varies by operation
- Response: 400 { code: "duplicate_resource" | "resource_not_found" | "resource_in_use", message: string }

**Acceptance Criteria:**
- 400 for duplicate permission names
- 400 for permission not found
- 400 for permission-in-use conflicts

---

Task: [API][SUCCESS] - Assign User Roles
// GIVEN an admin and target user
// WHEN POST/DELETE /auth/users/{id}/roles
// THEN 200 with updated roles

**API Specification:**
- Endpoint: POST /auth/users/{id}/roles, DELETE /auth/users/{id}/roles
- Authentication: Admin Required
- Request: { role_ids: array }
- Response: 200 { code: "success", data: { roles: array } }

**Acceptance Criteria:**
- Idempotent assignments
- Immediate effect on reads

---

Task: [API][FAIL][REQUEST] - User Role Assignment Request Errors
// GIVEN malformed request data
// WHEN assigning user roles
// THEN 400 with validation errors

**API Specification:**
- Endpoint: POST /auth/users/{id}/roles, DELETE /auth/users/{id}/roles
- Authentication: Admin Required
- Request: { role_ids: array }
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- 400 for missing or invalid role_ids

---

Task: [API][FAIL][PROFILE] - User Role Assignment Data Errors
// GIVEN invalid user or role references
// WHEN assigning user roles
// THEN 400 with data errors

**API Specification:**
- Endpoint: POST /auth/users/{id}/roles, DELETE /auth/users/{id}/roles
- Authentication: Admin Required
- Request: { role_ids: array }
- Response: 400 { code: "resource_not_found", message: string }

**Acceptance Criteria:**
- 400 for user not found
- 400 for role not found

---

Task: [API][SUCCESS] - Assign Permissions
// GIVEN an admin and target (user or role)
// WHEN POST/DELETE assignment endpoints
// THEN 200 with updated permissions

**API Specification:**
- Endpoint: POST /auth/users/{id}/permissions, POST /auth/roles/{id}/permissions
- Authentication: Admin Required
- Request: { permission_ids: array }
- Response: 200 { code: "success", data: { permissions: array } }

**Acceptance Criteria:**
- Support user-permission and role-permission flows

---

Task: [API][FAIL][REQUEST] - Permission Assignment Request Errors
// GIVEN malformed request data
// WHEN assigning permissions
// THEN 400 with validation errors

**API Specification:**
- Endpoint: POST /auth/users/{id}/permissions, POST /auth/roles/{id}/permissions
- Authentication: Admin Required
- Request: { permission_ids: array }
- Response: 400 { code: "invalid_request", message: string }

**Acceptance Criteria:**
- 400 for missing or invalid permission_ids

---

Task: [API][FAIL][PROFILE] - Permission Assignment Data Errors
// GIVEN invalid entity or permission references
// WHEN assigning permissions
// THEN 400 with data errors

**API Specification:**
- Endpoint: POST /auth/users/{id}/permissions, POST /auth/roles/{id}/permissions
- Authentication: Admin Required
- Request: { permission_ids: array }
- Response: 400 { code: "resource_not_found", message: string }

**Acceptance Criteria:**
- 400 for user/role not found
- 400 for permission not found