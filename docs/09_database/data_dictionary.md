# WellNexa AI — Complete Data Dictionary

## 1. Table: `users`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key, default `uuid_generate_v4()` | Unique user identifier |
| `email` | `VARCHAR(255)` | Unique, Not Null, Index | User login email address |
| `hashed_password`| `VARCHAR(255)` | Not Null | Argon2 / bcrypt password hash |
| `is_active` | `BOOLEAN` | Default `true`, Not Null | Account status flag |
| `is_verified` | `BOOLEAN` | Default `false`, Not Null | Email verification status |
| `created_at` | `TIMESTAMPTZ` | Default `now()`, Not Null | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | Default `now()`, Not Null | Last update timestamp |

## 2. Table: `profiles`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | Profile record ID |
| `user_id` | `UUID` | Unique, Foreign Key (`users.id` CASCADE) | References user |
| `first_name` | `VARCHAR(100)` | Not Null | User's first name |
| `last_name` | `VARCHAR(100)` | Not Null | User's last name |
| `date_of_birth` | `DATE` | Nullable | Birth date for age calculations |
| `gender` | `VARCHAR(20)` | Nullable | Gender enumeration |
| `blood_group` | `VARCHAR(20)` | Nullable | Blood group enumeration |
| `height_cm` | `FLOAT` | Nullable | Height in centimeters |
| `weight_kg` | `FLOAT` | Nullable | Weight in kilograms |

## 3. Table: `health_metrics`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | Metric entry ID |
| `user_id` | `UUID` | Foreign Key (`users.id` CASCADE), Index | References patient |
| `metric_type` | `VARCHAR(50)` | Not Null, Index | Metric type (`BMI`, `BLOOD_PRESSURE_SYSTOLIC`, etc.) |
| `value` | `FLOAT` | Not Null | Numeric value recorded |
| `unit` | `VARCHAR(30)` | Not Null | Measurement unit (`kg`, `mg/dL`, `mmHg`) |
| `source` | `VARCHAR(50)` | Default `MANUAL_ENTRY` | Data origin (`MANUAL_ENTRY`, `LAB_REPORT_OCR`) |
| `recorded_at` | `TIMESTAMPTZ` | Not Null, Index | Measurement timestamp |

## 4. Table: `patient_access_grants`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key | Grant record ID |
| `patient_id` | `UUID` | Foreign Key (`users.id` CASCADE), Index | Sharing patient |
| `doctor_id` | `UUID` | Foreign Key (`users.id` SET NULL), Nullable | Assigned doctor (optional) |
| `access_token` | `VARCHAR(100)` | Unique, Not Null, Index | Cryptographically secure token |
| `access_scope` | `VARCHAR(50)` | Not Null, Default `FULL_ACCESS` | Permission scope |
| `expires_at` | `TIMESTAMPTZ` | Not Null, Index | Expiration timestamp |
| `status` | `VARCHAR(50)` | Not Null, Default `ACTIVE`, Index | Status (`ACTIVE`, `EXPIRED`, `REVOKED`) |
