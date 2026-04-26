# BIT306 Project - Comprehensive Requirements & Progress Breakdown

## 📊 ASSESSMENT STRUCTURE

### Individual Marks: 54 Marks Total
| Topic | Marks | Student Allocation | Status |
|-------|-------|------------------|--------|
| **Topic 7: Enterprise Security** | 14M | Student 1 OR 2 | ✅ DONE |
| **Topic 8: RESTful APIs** | 13M | Student 1 OR 2 | 🔧 IN PROGRESS |
| **Topic 9: State Management & Caching** | 13M | Student 1 OR 2 | ⏳ TODO |
| **Topic 13: Testing & QA** | 14M | Each student min 1 test | ⏳ TODO |
| **INDIVIDUAL TOTAL** | **54M** | - | - |

### Group Marks: 46 Marks Total
| Topic | Marks | Task Type | Status |
|-------|-------|-----------|--------|
| **Topic 10: Async Processing** | 13M | Group Task | ⏳ TODO |
| **Topic 11: Microservices** | 12M | Group Task | ⏳ TODO |
| **Topic 12: Cloud Deployment** | 13M | Group Task | ⏳ TODO |
| **Case Study Discussion** | 8M | Group/Individual | ⏳ TODO |
| **GROUP TOTAL** | **46M** | - | - |

**GRAND TOTAL: 100 Marks**

---

## ✅ COMPLETED WORK

### Topic 7: Enterprise Security (14M) ✅

**What Was Done:**
- SQL Injection Prevention (5-layer defense)
- XSS Prevention (multi-layer)
- CSRF Protection (Django built-in)
- Secure Sessions (8hr timeout, HTTP-only)
- Brute-Force Protection (5 attempts)
- Input Validation (all forms)
- Query Monitoring & Logging
- 21 Security Tests (ALL PASSING)

**Files Created:**
- `accounts/validators.py` - SQL/XSS validators
- `accounts/tests/test_security.py` - Security tests
- `ngo_management/middleware.py` - Security middleware
- `SECURITY_IMPLEMENTATION.md` - Full documentation

**Marks Expected: 14/14** ✅

---

## 🔧 CURRENT ISSUE: Topic 8 (RESTful APIs) - 13 Marks

**API Tests Failing** - Need to fix:
1. Serializer issues
2. ViewSet issues
3. Permission issues
4. URL routing issues

**What Still Needs to Be Done:**

### 8.1 Create APIs for:
- ✅ NGO management (CRUD endpoints)
- ✅ Activity listing (with filtering)
- ✅ Registration (create/cancel)
- ⏳ **Fix test failures**

### 8.2 Follow REST Principles:
- ✅ GET → retrieve data
- ✅ POST → create
- ✅ PUT/PATCH → update
- ✅ DELETE → remove

### 8.3 API Features:
- ✅ JSON responses
- ✅ Validation
- ✅ Pagination
- ✅ Filtering (date, location)
- ⏳ **Test & verify all working**

### 8.4 API Versioning:
- ✅ `/api/v1/` endpoints

---

## ⏳ TODO ITEMS (In Order of Priority)

### PRIORITY 1: Fix Topic 8 API Tests (Required for marks)
1. Debug test failures
2. Fix serializers/viewsets
3. Verify all API endpoints work
4. Create Postman collection
5. **Expected: 13/13 marks**

### PRIORITY 2: Topic 13 - Testing & QA (14 Marks)
**Each student must do minimum:**
- Unit Tests (registration logic, etc.)
- API Tests (Postman collection)
- Integration Tests (API + database)

**Implementation:**
- `accounts/tests/test_security.py` - ✅ DONE (21 tests)
- `ngo/tests/test_api.py` - ⏳ TODO
- `registration/tests/test_integration.py` - ⏳ TODO

### PRIORITY 3: Topic 9 - Caching (13 Marks)
**Session Handling (split between 2 students):**
- Student 1: Admin login session handling ⏳
- Student 2: Employee login session handling ⏳

**Caching (split between 2 students):**
- Student 1: Cache NGO listing ⏳
- Student 2: Cache participants listing ⏳

**Implementation Required:**
- Redis installation & configuration
- Django cache backend setup
- Cache invalidation logic
- Performance comparison (before/after)

### PRIORITY 4: Group Tasks (46 Marks)

#### Topic 10: Async Processing (13M)
- **What to do:**
  - Setup Redis/RabbitMQ
  - Setup Celery
  - Email reminders (background job)
  - Real-time notifications (bonus)

#### Topic 11: Microservices (12M)
- **What to do:**
  - User Service
  - NGO Service
  - Registration Service
  - API Gateway pattern
  - REST communication between services

#### Topic 12: Cloud Deployment (13M)
- **What to do:**
  - Docker containerization
  - Docker Compose
  - Environment variables (`.env`)
  - GitHub Actions for CI/CD
  - Deploy to Render/Railway (not AWS)

#### Case Study Discussion (8M)
- Explain system features
- Identify key actors
- Describe workflows
- Handle edge cases

---

## 📋 RECOMMENDED EXECUTION PLAN

### Week 1: Individual Tasks
```
Day 1-2: Fix Topic 8 API (Priority 1)
Day 3-4: Topic 13 Testing (Priority 2)
Day 5-7: Topic 9 Caching (Priority 3)
```

### Week 2: Group Tasks
```
Day 1-3: Topic 10 Async Processing
Day 4-5: Topic 11 Microservices
Day 6-7: Topic 12 Deployment + Case Study
```

---

## 🔍 CURRENT ERRORS TO FIX

**Test Command:** `python manage.py test accounts.tests.test_api_endpoints --verbosity=2`

**Expected Fixes:**
- Check serializers for field mismatches
- Verify ViewSet permissions
- Check URL routing
- Validate authentication setup

---

## 📝 SUBMISSION REQUIREMENTS

### Before Final Submission:
1. ✅ Project report (Word document)
2. ✅ Video presentation (MP4)
3. ✅ Source code (GitHub repo)
4. ✅ Database backup
5. ✅ Turnitin plagiarism report
6. ✅ Cloud deployment link (working URL)

### Report Must Include:
- User manuals for all features
- Which student completed which task
- Security explanation
- API documentation
- Testing results
- Caching performance comparison
- Deployment instructions

### Video Must Demonstrate:
- All 7 topics working
- Security features
- API endpoints
- Caching impact
- Deployment process

---

## 🎯 MARKS BREAKDOWN

### To Get 80+ Marks (Excellent):

**Individual (54 marks):**
- Topic 7: 13-14/14 (comprehensive OWASP implementation)
- Topic 8: 12-13/13 (fully REST-compliant, well-documented)
- Topic 9: 12-13/13 (secure sessions, Redis caching with metrics)
- Topic 13: 13-14/14 (comprehensive test coverage)

**Group (46 marks):**
- Topic 10: 12-13/13 (Celery + real-time notifications)
- Topic 11: 11-12/12 (clean microservices architecture)
- Topic 12: 12-13/13 (Docker + full CI/CD pipeline)
- Case Study: 7-8/8 (complete system understanding)

**TOTAL: 95-100/100 marks**

---

## ⚡ NEXT STEPS

**IMMEDIATE:**
1. Fix API test failures (Topic 8)
2. Run: `python manage.py runserver` to verify no import errors
3. Test API endpoints manually
4. Create Postman collection

**THEN:**
1. Implement comprehensive tests (Topic 13)
2. Add caching with Redis (Topic 9)
3. Setup Celery for async tasks (Topic 10)
4. Design microservices (Topic 11)
5. Deploy to cloud (Topic 12)

---

## 📞 KEY POINTS FOR LECTURERS

**Show them:**
1. Security tests passing ✅
2. API endpoints documented
3. Test coverage metrics
4. Performance improvements (caching)
5. CI/CD pipeline working
6. Application deployed & running
7. Each student's contribution documented

