# Software Requirements Specification (SRS)

## Traffic Management System (TMS)

**Version:** 1.0  
**Date:** October 31, 2025  
**Project:** Real-time Traffic Monitoring and Adaptive Signal Control System

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features](#3-system-features)
4. [External Interface Requirements](#4-external-interface-requirements)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [System Architecture](#7-system-architecture)
8. [Data Requirements](#8-data-requirements)
9. [Appendices](#9-appendices)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document provides a complete description of the Traffic Management System (TMS). The system is designed to monitor real-time traffic conditions, detect incidents, optimize signal timings, and provide analytics for traffic operators and administrators.

### 1.2 Scope

The Traffic Management System includes:

- Real-time vehicle detection and counting using computer vision
- Dynamic traffic signal optimization
- Incident detection and management
- Interactive web dashboard for monitoring and control
- Analytics and reporting capabilities
- Multi-user role support (Operators, Admins, Emergency Services)

### 1.3 Definitions, Acronyms, and Abbreviations

- **TMS**: Traffic Management System
- **MVP**: Minimum Viable Product
- **API**: Application Programming Interface
- **KPI**: Key Performance Indicator
- **CV**: Computer Vision
- **REST**: Representational State Transfer
- **WebSocket**: Full-duplex communication protocol
- **MTTA**: Mean Time To Acknowledge
- **MTTR**: Mean Time To Resolve

### 1.4 References

- IEEE 830-1998 Standard for Software Requirements Specifications
- Traffic Control Systems Handbook
- OpenCV Documentation v4.12.0
- React Documentation v18.2.0

### 1.5 Overview

This document describes the functional and non-functional requirements, system architecture, data models, and interfaces for the Traffic Management System.

---

## 2. Overall Description

### 2.1 Product Perspective

The TMS is a standalone web-based system that integrates:

- **Backend Services**: Python/Flask for video processing and traffic analysis
- **Frontend Dashboard**: React-based responsive web interface
- **Real-time Communication**: WebSocket for live updates
- **Database**: SQLite/PostgreSQL for data persistence
- **Detection System**: OpenCV-based vehicle detection from video feeds

### 2.2 Product Functions

The system provides the following major functions:

#### For City Traffic Operators:

- **FR-001**: Monitor real-time traffic data from all intersections
- **FR-002**: Manual override of signal timings
- **FR-003**: Report traffic incidents
- **FR-004**: Acknowledge and clear incidents

#### For Traffic Engineer/Admin:

- **FR-005**: Configure intersection parameters
- **FR-006**: View analytics and KPIs
- **FR-007**: Manage signal timing plans
- **FR-008**: Generate reports (daily, weekly, monthly)

#### For Emergency Services:

- **FR-009**: Request signal preemption for emergency routes
- **FR-010**: View real-time traffic conditions
- **FR-011**: Receive priority routing recommendations

### 2.3 User Classes and Characteristics

| User Class              | Technical Expertise | Primary Functions                                    |
| ----------------------- | ------------------- | ---------------------------------------------------- |
| City Traffic Operator   | Moderate            | Monitor traffic, manual control, incident management |
| Traffic Engineer/Admin  | High                | System configuration, analytics, planning            |
| Emergency Services      | Low-Moderate        | Preemption requests, route monitoring                |
| General Public (Future) | Low                 | View traffic conditions, travel time estimates       |

### 2.4 Operating Environment

- **Server OS**: Windows/Linux
- **Client Browser**: Chrome 90+, Firefox 88+, Edge 90+, Safari 14+
- **Python Version**: 3.13+
- **Node.js Version**: 16+
- **Network**: Local network or internet connection
- **Hardware**: Minimum 8GB RAM, 4-core CPU for video processing

### 2.5 Design and Implementation Constraints

- Must process video at minimum 5 FPS for vehicle detection
- Response time for dashboard updates: < 2 seconds
- System uptime: 99.5% availability
- Support for up to 50 concurrent intersections
- All data must be stored securely with audit trails

### 2.6 Assumptions and Dependencies

- Video feeds are available in MP4 format
- Network connectivity is stable
- Users have appropriate authentication credentials
- Modern web browsers with JavaScript enabled

---

## 3. System Features

### 3.1 Real-time Traffic Monitoring (UC-001)

**Priority**: High  
**Description**: Continuously monitor traffic conditions at all configured intersections.

**Functional Requirements**:

- **FR-001.1**: System shall process video feeds to detect and count vehicles
- **FR-001.2**: System shall update traffic counts every 2 seconds
- **FR-001.3**: System shall calculate road density (vehicles/segment)
- **FR-001.4**: System shall display live traffic graph with color-coded edges
- **FR-001.5**: System shall preserve zoom/pan state during updates

**Use Case Flow**:

1. Operator opens dashboard
2. System displays network graph with intersections and road segments
3. Backend processes video frames every 2 seconds
4. Vehicle counts updated and transmitted via WebSocket
5. Dashboard reflects updated traffic density with visual indicators

### 3.2 Adaptive Signal Control (UC-002)

**Priority**: High  
**Description**: Automatically optimize signal timings based on current traffic conditions.

**Functional Requirements**:

- **FR-002.1**: System shall collect detector data from all approaches
- **FR-002.2**: System shall estimate queue lengths using occupancy data
- **FR-002.3**: System shall compute optimal green splits using adaptive algorithm
- **FR-002.4**: System shall enforce min/max green time constraints
- **FR-002.5**: System shall apply new signal plan to intersection
- **FR-002.6**: System shall broadcast state changes via WebSocket
- **FR-002.7**: System shall log cycle and metrics for auditing

**Control Loop Cycle**:

```
Start Cycle → Collect Data → Estimate Queues → Compute Splits →
Check Constraints → Apply Plan → Broadcast State → Log Metrics →
Wait for Next Cycle
```

### 3.3 Manual Override Control (UC-003)

**Priority**: Medium  
**Description**: Allow operators to manually control signal timings.

**Functional Requirements**:

- **FR-003.1**: System shall provide manual override interface
- **FR-003.2**: Operator can set custom green/red durations
- **FR-003.3**: System shall validate timing constraints
- **FR-003.4**: System shall log all manual overrides with timestamp and user
- **FR-003.5**: System shall allow return to automatic mode

### 3.4 Incident Management (UC-004)

**Priority**: High  
**Description**: Report, track, and resolve traffic incidents.

**Functional Requirements**:

- **FR-004.1**: Operator can create incident with type, location, severity
- **FR-004.2**: System shall insert incident record to database
- **FR-004.3**: System shall generate unique incident ID
- **FR-004.4**: System shall broadcast new incident alert to dashboard
- **FR-004.5**: Operator can acknowledge incident
- **FR-004.6**: System shall update status to "Acknowledged"
- **FR-004.7**: System shall calculate MTTA (Mean Time To Acknowledge)
- **FR-004.8**: Operator can resolve incident
- **FR-004.9**: System shall calculate MTTR (Mean Time To Resolve)
- **FR-004.10**: System shall maintain complete audit trail

**Incident Workflow**:

```
Create → Insert DB → Broadcast Alert → Display Badge →
Acknowledge → Update Status → Notify Resolution → Update Panel →
Log Metrics
```

### 3.5 Configuration Management (UC-005)

**Priority**: Medium  
**Description**: Configure intersections, phases, and timing plans.

**Functional Requirements**:

- **FR-005.1**: Admin can define intersection properties (name, location)
- **FR-005.2**: Admin can configure signal phases with timing ranges
- **FR-005.3**: System shall validate phase sequences
- **FR-005.4**: Admin can create/modify signal timing plans
- **FR-005.5**: System shall store configurations in database
- **FR-005.6**: Changes shall be logged with timestamp and user

### 3.6 Analytics and Reporting (UC-006)

**Priority**: Medium  
**Description**: Generate analytics, KPIs, and performance reports.

**Functional Requirements**:

- **FR-006.1**: System shall display real-time KPIs on dashboard
- **FR-006.2**: System shall track average wait times per intersection
- **FR-006.3**: System shall calculate throughput metrics
- **FR-006.4**: System shall generate incident reports (MTTA/MTTR)
- **FR-006.5**: Admin can export reports in CSV/JSON format
- **FR-006.6**: System shall provide historical trend analysis

### 3.7 Emergency Preemption (UC-007)

**Priority**: High  
**Description**: Allow emergency services to request signal priority.

**Functional Requirements**:

- **FR-007.1**: Emergency user can request preemption for specific route
- **FR-007.2**: System shall override normal signal timing
- **FR-007.3**: System shall provide green wave along emergency route
- **FR-007.4**: System shall notify operators of active preemption
- **FR-007.5**: System shall log all preemption requests
- **FR-007.6**: System shall return to normal operation after emergency passes

### 3.8 User Authentication (UC-008)

**Priority**: High  
**Description**: Secure user login with role-based access control.

**Functional Requirements**:

- **FR-008.1**: Users must login with username and password
- **FR-008.2**: System shall validate credentials against database
- **FR-008.3**: System shall assign role (Operator/Admin/Emergency)
- **FR-008.4**: System shall restrict features based on user role
- **FR-008.5**: System shall log all login attempts
- **FR-008.6**: System shall enforce session timeout after 30 minutes

---

## 4. External Interface Requirements

### 4.1 User Interfaces

#### 4.1.1 Dashboard Layout

- **Header**: Application title, user info, notifications
- **Main Area**: Interactive traffic network graph
- **Left Sidebar**: Info panels with current statistics
- **Map Background**: Google Maps-style grid pattern (#e5e3df)
- **Color Scheme**: Google blue (#1a73e8), white panels, dark text (#202124)

#### 4.1.2 Traffic Graph Visualization

- **Nodes**: Circular junction markers (size: 15px)
- **Edges**: Lines representing road segments
- **Edge Colors**:
  - Green: Low traffic (0-5 vehicles)
  - Yellow: Medium traffic (6-10 vehicles)
  - Orange: High traffic (11-15 vehicles)
  - Red: Congested (16+ vehicles)
- **Edge Width**: Proportional to traffic density
- **Labels**: Junction names and vehicle counts

#### 4.1.3 Control Panels

- **Traffic Info Panel**: Current statistics, junction details
- **Incident Panel**: Active incidents with severity badges
- **Control Panel**: Signal override controls (Admin only)
- **Analytics Panel**: KPIs and performance metrics

#### 4.1.4 Responsive Design

- Desktop: Full-featured layout (1920x1080 optimal)
- Tablet: Collapsible sidebar (768px-1024px)
- Mobile: Stacked layout (320px-767px)

### 4.2 Hardware Interfaces

- **Video Input**: MP4 video files (timelapse format)
- **Camera Support**: Future integration with IP cameras
- **Detector Hardware**: Optional loop detectors/radar sensors

### 4.3 Software Interfaces

#### 4.3.1 Backend API (Flask)

- **Protocol**: HTTP/REST
- **Base URL**: `http://127.0.0.1:5000`
- **Endpoints**:
  - `GET /api/graph_data` - Retrieve current traffic graph
  - `POST /api/incident` - Create new incident
  - `PUT /api/incident/:id` - Update incident status
  - `GET /api/analytics` - Retrieve KPIs and metrics
  - `POST /api/override` - Manual signal override
  - `GET /api/config` - Get intersection configuration
  - `PUT /api/config` - Update configuration

#### 4.3.2 WebSocket Interface

- **Protocol**: WebSocket
- **URL**: `ws://127.0.0.1:5000/ws`
- **Events**:
  - `traffic_update` - Real-time traffic data
  - `incident_alert` - New incident notification
  - `signal_change` - Signal state update
  - `config_update` - Configuration change notification

#### 4.3.3 Database Interface

- **Type**: SQLite (dev) / PostgreSQL (production)
- **ORM**: SQLAlchemy (optional)
- **Tables**:
  - `intersections` - Intersection master data
  - `phases` - Signal phase configurations
  - `plans` - Timing plan definitions
  - `incidents` - Incident records
  - `users` - User accounts and roles
  - `audit_log` - System audit trail
  - `metrics` - Performance metrics

#### 4.3.4 External Libraries

- **Backend**:
  - Flask 3.0.0 - Web framework
  - Flask-CORS 4.0.0 - Cross-origin support
  - OpenCV 4.12.0 - Computer vision
  - NumPy 2.2.6 - Numerical processing
  - NetworkX 3.2.1 - Graph algorithms
- **Frontend**:
  - React 18.2.0 - UI framework
  - vis-network 9.1.9 - Graph visualization
  - Axios - HTTP client
  - Socket.io-client - WebSocket client

### 4.4 Communication Interfaces

- **Network Protocol**: TCP/IP
- **Data Format**: JSON
- **Authentication**: Token-based (JWT)
- **Encryption**: HTTPS (production)
- **Port Configuration**:
  - Backend: 5000
  - Frontend Dev: 3000
  - WebSocket: 5000

---

## 5. Functional Requirements

### 5.1 Data Processing Requirements

#### 5.1.1 Video Processing (FR-100)

- **FR-101**: System shall accept MP4 video files for each road segment
- **FR-102**: System shall extract frames at configurable interval (default: 5 frames)
- **FR-103**: System shall loop video continuously for continuous monitoring
- **FR-104**: System shall handle 15 concurrent video segments
- **FR-105**: System shall process minimum 1 frame per second per segment

#### 5.1.2 Vehicle Detection (FR-200)

- **FR-201**: System shall convert frames to grayscale
- **FR-202**: System shall apply Gaussian blur (7x7 kernel)
- **FR-203**: System shall perform Canny edge detection (threshold: 80-200)
- **FR-204**: System shall detect contours from edge image
- **FR-205**: System shall filter contours by area (minimum: 400 pixels)
- **FR-206**: System shall count valid contours as vehicles
- **FR-207**: Detection accuracy shall be ≥ 85%

#### 5.1.3 Traffic Analysis (FR-300)

- **FR-301**: System shall calculate road density per segment
- **FR-302**: System shall identify congestion patterns
- **FR-303**: System shall estimate queue lengths
- **FR-304**: System shall predict traffic trends (future enhancement)
- **FR-305**: System shall update metrics every 2 seconds

### 5.2 Signal Control Requirements

#### 5.2.1 Adaptive Algorithm (FR-400)

- **FR-401**: System shall aggregate detector arrivals (last 60s window)
- **FR-402**: System shall estimate queue lengths from occupancy
- **FR-403**: System shall compute optimal splits to minimize C - last_time
- **FR-404**: System shall enforce safety bounds (g_min ≤ g ≤ g_max)
- **FR-405**: System shall apply signal plan via phase commands
- **FR-406**: System shall validate phase sequences for conflicts
- **FR-407**: Algorithm cycle time: ≤ 1 second

#### 5.2.2 Timing Constraints (FR-500)

- **FR-501**: Minimum green time: 5 seconds (configurable)
- **FR-502**: Maximum green time: 60 seconds (configurable)
- **FR-503**: Yellow interval: 3-5 seconds
- **FR-504**: All-red clearance: 2 seconds
- **FR-505**: Cycle length: 60-180 seconds
- **FR-506**: Phase transition time: ≤ 0.5 seconds

### 5.3 Data Management Requirements

#### 5.3.1 Data Storage (FR-600)

- **FR-601**: System shall persist all intersection configurations
- **FR-602**: System shall store incident records indefinitely
- **FR-603**: System shall retain metrics for minimum 90 days
- **FR-604**: System shall backup database daily
- **FR-605**: System shall support data export (CSV/JSON)

#### 5.3.2 Data Integrity (FR-700)

- **FR-701**: All database operations shall be ACID-compliant
- **FR-702**: System shall validate data before insertion
- **FR-703**: System shall prevent duplicate incident IDs
- **FR-704**: System shall maintain referential integrity
- **FR-705**: System shall log all data modifications

### 5.4 User Interface Requirements

#### 5.4.1 Dashboard (FR-800)

- **FR-801**: Dashboard shall load within 3 seconds
- **FR-802**: Graph shall support zoom and pan
- **FR-803**: Graph shall preserve viewport during updates
- **FR-804**: Updates shall occur every 1 second (frontend polling)
- **FR-805**: Node size: 15px, edge width: 1-5px
- **FR-806**: Color coding shall be intuitive and consistent

#### 5.4.2 Controls (FR-900)

- **FR-901**: All forms shall have input validation
- **FR-902**: Submit buttons shall be disabled during processing
- **FR-903**: Success/error messages shall be displayed clearly
- **FR-904**: Confirmation required for destructive actions
- **FR-905**: Help text available for all controls

---

## 6. Non-Functional Requirements

### 6.1 Performance Requirements

#### 6.1.1 Response Time

- **NFR-101**: API response time ≤ 500ms (95th percentile)
- **NFR-102**: WebSocket message delivery ≤ 100ms
- **NFR-103**: Dashboard refresh latency ≤ 2 seconds
- **NFR-104**: Video frame processing ≤ 200ms per frame
- **NFR-105**: Database query time ≤ 100ms

#### 6.1.2 Throughput

- **NFR-201**: Support 100 concurrent dashboard users
- **NFR-202**: Process 15 video streams simultaneously
- **NFR-203**: Handle 1000 API requests per minute
- **NFR-204**: Support 50 active intersections

#### 6.1.3 Capacity

- **NFR-301**: Store 1 million incident records
- **NFR-302**: Retain 90 days of metrics (≈ 10GB)
- **NFR-303**: Support 1000 user accounts
- **NFR-304**: Handle 100 concurrent WebSocket connections

### 6.2 Reliability Requirements

#### 6.2.1 Availability

- **NFR-401**: System uptime: 99.5% (excluding maintenance)
- **NFR-402**: Maximum unplanned downtime: 4 hours/month
- **NFR-403**: Planned maintenance window: 2 hours/week
- **NFR-404**: Graceful degradation during partial failures

#### 6.2.2 Fault Tolerance

- **NFR-501**: System shall recover from video processing errors
- **NFR-502**: Database connection failures shall retry (max 3 attempts)
- **NFR-503**: WebSocket disconnections shall auto-reconnect
- **NFR-504**: Invalid data shall be logged and rejected

#### 6.2.3 Data Backup

- **NFR-601**: Daily automated database backups
- **NFR-602**: Backup retention: 30 days
- **NFR-603**: Recovery Time Objective (RTO): 4 hours
- **NFR-604**: Recovery Point Objective (RPO): 24 hours

### 6.3 Security Requirements

#### 6.3.1 Authentication

- **NFR-701**: All users must authenticate to access system
- **NFR-702**: Password minimum length: 8 characters
- **NFR-703**: Password must include uppercase, lowercase, number, special char
- **NFR-704**: Account lockout after 5 failed login attempts
- **NFR-705**: Session timeout: 30 minutes of inactivity

#### 6.3.2 Authorization

- **NFR-801**: Role-based access control (RBAC) enforced
- **NFR-802**: Operators: monitor, report, acknowledge
- **NFR-803**: Admins: full configuration and analytics access
- **NFR-804**: Emergency: preemption requests only
- **NFR-805**: Least privilege principle applied

#### 6.3.3 Data Protection

- **NFR-901**: Sensitive data encrypted at rest (AES-256)
- **NFR-902**: HTTPS required for production deployment
- **NFR-903**: SQL injection prevention via parameterized queries
- **NFR-904**: XSS protection enabled on all inputs
- **NFR-905**: CSRF tokens on all state-changing operations

#### 6.3.4 Audit Trail

- **NFR-1001**: All user actions logged with timestamp, user, action
- **NFR-1002**: Incident lifecycle fully auditable
- **NFR-1003**: Configuration changes tracked
- **NFR-1004**: Logs retained for minimum 1 year
- **NFR-1005**: Logs write-protected from modification

### 6.4 Usability Requirements

#### 6.4.1 User Experience

- **NFR-1101**: Interface shall follow Google Material Design guidelines
- **NFR-1102**: Color scheme accessible (WCAG AA compliance)
- **NFR-1103**: Responsive design for desktop/tablet/mobile
- **NFR-1104**: Help documentation available online
- **NFR-1105**: Tooltips on all non-obvious controls

#### 6.4.2 Learning Curve

- **NFR-1201**: New operators trained in ≤ 4 hours
- **NFR-1202**: Admins trained in ≤ 8 hours
- **NFR-1203**: User manual provided
- **NFR-1204**: Video tutorials available

### 6.5 Maintainability Requirements

#### 6.5.1 Code Quality

- **NFR-1301**: Code commented and documented
- **NFR-1302**: Modular architecture with separation of concerns
- **NFR-1303**: Consistent naming conventions
- **NFR-1304**: Version control using Git
- **NFR-1305**: Unit test coverage ≥ 70%

#### 6.5.2 Monitoring

- **NFR-1401**: System health dashboard available
- **NFR-1402**: Error logging with stack traces
- **NFR-1403**: Performance metrics tracked (CPU, memory, network)
- **NFR-1404**: Alert notifications for critical errors

### 6.6 Portability Requirements

#### 6.6.1 Platform Independence

- **NFR-1501**: Backend runs on Windows/Linux/macOS
- **NFR-1502**: Frontend compatible with Chrome, Firefox, Edge, Safari
- **NFR-1503**: Database supports SQLite and PostgreSQL
- **NFR-1504**: Docker containerization supported

### 6.7 Scalability Requirements

#### 6.7.1 Horizontal Scaling

- **NFR-1601**: Architecture supports load balancing
- **NFR-1602**: Stateless API design for multi-instance deployment
- **NFR-1603**: Database connection pooling implemented
- **NFR-1604**: WebSocket connections distributable

#### 6.7.2 Vertical Scaling

- **NFR-1701**: Efficient memory usage (< 2GB per instance)
- **NFR-1702**: CPU utilization < 80% under normal load
- **NFR-1703**: Optimized database queries (indexed)

---

## 7. System Architecture

### 7.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Operator   │  │ Traffic Eng. │  │  Emergency   │  │
│  │     UI       │  │   Admin UI   │  │  Services UI │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS / WebSocket
┌───────────────────────┴─────────────────────────────────┐
│                  Presentation Layer                      │
│              Browser Dashboard (React)                   │
│  ┌────────────────────────────────────────────────┐     │
│  │  Traffic Graph │ Info Panels │ Control Forms   │     │
│  └────────────────────────────────────────────────┘     │
└───────────────────────┬─────────────────────────────────┘
                        │ REST API / WebSocket
┌───────────────────────┴─────────────────────────────────┐
│                  Application Layer                       │
│                TMS Backend (Flask)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Incident   │  │   Adaptive   │  │   Config     │  │
│  │  Management  │  │  Optimizer   │  │  Manager     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Detector   │  │   Metrics    │  │  WebSocket   │  │
│  │  Simulator   │  │  Analytics   │  │  Broadcast   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                  Processing Layer                        │
│         Video Processing & CV (OpenCV)                   │
│  ┌────────────────────────────────────────────────┐     │
│  │  Frame Extract │ Detection │ Count │ Analyze   │     │
│  └────────────────────────────────────────────────┘     │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                    Data Layer                            │
│  ┌──────────────┐                  ┌──────────────┐     │
│  │   Database   │                  │    Video     │     │
│  │ (SQLite/PG)  │                  │    Files     │     │
│  └──────────────┘                  └──────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Component Descriptions

#### 7.2.1 P1: Detector / Simulator

- **Purpose**: Ingest and validate detector/video data
- **Inputs**: Video files, sensor feeds
- **Outputs**: Vehicle counts, occupancy metrics
- **Processing**: Frame extraction, CV detection, data validation

#### 7.2.2 P2: Adaptive Optimization

- **Purpose**: Compute optimal signal timings
- **Inputs**: Queue estimates, current phase state, constraints
- **Outputs**: Phase/split decisions, green time allocations
- **Algorithm**: Queue-based optimization with safety bounds

#### 7.2.3 P3: Manual / Preemption Control

- **Purpose**: Handle operator overrides and emergency preemption
- **Inputs**: Override commands, preemption requests
- **Outputs**: Signal commands, status updates
- **Validation**: Constraint checking, conflict detection

#### 7.2.4 P4: Incident Management

- **Purpose**: Track and resolve traffic incidents
- **Inputs**: Incident reports, acknowledgments
- **Outputs**: Incident logs, alerts, metrics (MTTA/MTTR)
- **Storage**: D3: Incidents database

#### 7.2.5 P5: Reporting & Analytics

- **Purpose**: Generate KPIs and performance reports
- **Inputs**: Metrics, incidents, control logs
- **Outputs**: Daily KPIs, CSV/JSON reports
- **Analysis**: Statistical aggregation, trend detection

#### 7.2.6 P6: Realtime Broadcast (WebSocket)

- **Purpose**: Push live updates to dashboard
- **Inputs**: State changes, alerts, metrics
- **Outputs**: WebSocket messages to connected clients
- **Protocol**: Socket.io / native WebSocket

### 7.3 Data Stores

#### 7.3.1 D1: Raw/Validated Detector Data

- **Type**: Time-series data
- **Schema**: timestamp, intersection_id, approach_id, count, occupancy
- **Retention**: 60 seconds (rolling window)

#### 7.3.2 D2: Config & Plans

- **Type**: Relational tables
- **Schema**: intersections, phases, plans, constraints
- **Persistence**: Permanent

#### 7.3.3 D3: Incidents

- **Type**: Relational table
- **Schema**: id, intersection_id, type, severity, status, reported_by, ack_time
- **Persistence**: Permanent with archival

#### 7.3.4 D4: Audit & Metrics

- **Type**: Append-only logs
- **Schema**: timestamp, user, action, parameters, result
- **Retention**: 90 days

### 7.4 Data Flow Diagrams

#### 7.4.1 DFD Level 0: Context Diagram

```
External Actors → TMS System → Audit & Metrics Store
- City Traffic Operator: commands, countermeasures
- Traffic Engineer Admin: configure intersections, plans
- Emergency Services: preemption requests
- Detectors/Simulator: counts, occupancy
```

#### 7.4.2 DFD Level 1: Major Processes

See reference diagram Fig. 7 for detailed process flows.

#### 7.4.3 DFD Level 2: Subsystem Details

- **Adaptive Control Loop**: Aggregate → Estimate → Compute → Enforce → Apply → Broadcast → Log
- **Incident Management**: Create → Assign → Acknowledge → Resolve → Alert → Complete Audit

---

## 8. Data Requirements

### 8.1 Data Models

#### 8.1.1 Intersection Entity

```python
class Intersection:
    id: int                    # Primary key
    name: string               # Intersection name
    location: string           # GPS coordinates or address
    current_plan_id: int       # Foreign key to Plan

    # Methods
    getActivePhases() -> list  # Returns active signal phases
```

#### 8.1.2 Phase Entity

```python
class Phase:
    id: int                    # Primary key
    intersection_id: int       # Foreign key to Intersection
    min_green: int             # Minimum green time (seconds)
    max_green: int             # Maximum green time (seconds)
    state: string              # Current state (red/yellow/green)
    last_updated: datetime     # Last state change timestamp
```

#### 8.1.3 Plan Entity

```python
class Plan:
    id: int                    # Primary key
    cycle_length: int          # Total cycle duration (seconds)
    phases: list               # List of phase configurations
    created_at: datetime       # Creation timestamp
```

#### 8.1.4 Detector Entity

```python
class Detector:
    id: int                    # Primary key
    approach_id: int           # Road approach identifier
    count: int                 # Current vehicle count
    occupancy: float           # Occupancy percentage (0-100)
    timestamp: datetime        # Last update time
```

#### 8.1.5 Incident Entity

```python
class Incident:
    id: int                    # Primary key
    intersection_id: int       # Foreign key to Intersection
    type: string               # Incident type (accident, construction, etc.)
    severity: string           # Severity level (low, medium, high, critical)
    status: string             # Status (reported, acknowledged, resolved)
    reported_by: string        # User who reported
    ack_time: datetime         # Acknowledgment timestamp
```

#### 8.1.6 User Entity

```python
class User:
    id: int                    # Primary key
    username: string           # Unique username
    role: string               # User role (operator, admin, emergency)
    email: string              # Email address

    # Methods
    login() -> bool            # Authenticate user
```

### 8.2 Database Schema (Relational)

```sql
-- Intersections table
CREATE TABLE intersections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    current_plan_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (current_plan_id) REFERENCES plans(id)
);

-- Phases table
CREATE TABLE phases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intersection_id INTEGER NOT NULL,
    phase_number INTEGER NOT NULL,
    min_green INTEGER DEFAULT 5,
    max_green INTEGER DEFAULT 60,
    state VARCHAR(20) DEFAULT 'red',
    last_updated TIMESTAMP,
    FOREIGN KEY (intersection_id) REFERENCES intersections(id)
);

-- Plans table
CREATE TABLE plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    cycle_length INTEGER DEFAULT 90,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detectors table
CREATE TABLE detectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intersection_id INTEGER NOT NULL,
    approach_id VARCHAR(50) NOT NULL,
    count INTEGER DEFAULT 0,
    occupancy REAL DEFAULT 0.0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (intersection_id) REFERENCES intersections(id)
);

-- Incidents table
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intersection_id INTEGER,
    type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'reported',
    reported_by VARCHAR(100),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Audit log table
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Metrics table
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intersection_id INTEGER,
    metric_type VARCHAR(50) NOT NULL,
    value REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (intersection_id) REFERENCES intersections(id)
);
```

### 8.3 API Data Formats

#### 8.3.1 Traffic Graph Response

```json
{
  "nodes": [
    {
      "id": "Start",
      "label": "Start",
      "x": 0,
      "y": 0,
      "size": 15,
      "color": "#1a73e8"
    }
  ],
  "edges": [
    {
      "from": "Start",
      "to": "R1",
      "label": "5 vehicles",
      "value": 5,
      "color": "#4caf50",
      "title": "Start → R1: 5 vehicles"
    }
  ],
  "timestamp": "2025-10-31T10:30:00Z"
}
```

#### 8.3.2 Incident Creation Request

```json
{
  "intersection_id": 1,
  "type": "accident",
  "severity": "high",
  "location": "Main St & 5th Ave",
  "description": "Two-vehicle collision blocking left lane",
  "reported_by": "operator_1"
}
```

#### 8.3.3 Incident Response

```json
{
  "id": 42,
  "intersection_id": 1,
  "type": "accident",
  "severity": "high",
  "status": "reported",
  "location": "Main St & 5th Ave",
  "reported_by": "operator_1",
  "reported_at": "2025-10-31T10:32:15Z",
  "acknowledged_at": null,
  "resolved_at": null
}
```

#### 8.3.4 Analytics KPI Response

```json
{
  "date": "2025-10-31",
  "intersections_monitored": 15,
  "total_vehicles": 12540,
  "average_density": 8.3,
  "incidents": {
    "total": 7,
    "by_severity": {
      "low": 3,
      "medium": 2,
      "high": 2,
      "critical": 0
    },
    "mtta": "00:03:45",
    "mttr": "00:18:32"
  },
  "signal_performance": {
    "avg_cycle_time": 95,
    "manual_overrides": 12,
    "preemptions": 3
  }
}
```

---

## 9. Appendices

### 9.1 Use Case Specifications

#### UC-001: Monitor Traffic Data

**Actor**: City Traffic Operator  
**Precondition**: Operator is logged in, system is running  
**Main Flow**:

1. Operator opens dashboard
2. System displays real-time traffic graph
3. System updates vehicle counts every 2 seconds
4. Operator observes traffic patterns
5. Operator can zoom/pan to view specific areas

**Postcondition**: Operator has current traffic awareness  
**Alternative Flows**: None  
**Exceptions**: Video feed unavailable → System displays "No data" message

#### UC-002: Manual Override Control

**Actor**: City Traffic Operator  
**Precondition**: Operator has override permissions  
**Main Flow**:

1. Operator selects intersection
2. Operator clicks "Manual Control"
3. System displays current phase timings
4. Operator adjusts green/red durations
5. System validates constraints
6. Operator confirms changes
7. System applies new timings
8. System logs override action

**Postcondition**: Custom signal timing is active  
**Alternative Flows**:

- 5a. Validation fails → Display error, return to step 4
  **Exceptions**: Database error → Rollback, display error message

#### UC-004: Report Incident

**Actor**: City Traffic Operator  
**Precondition**: Operator is logged in  
**Main Flow**:

1. Operator clicks "Report Incident"
2. System displays incident form
3. Operator enters type, location, severity
4. Operator submits form
5. System validates input
6. System inserts incident to database
7. System broadcasts alert to dashboard
8. System displays confirmation

**Postcondition**: Incident is recorded and visible  
**Alternative Flows**:

- 5a. Validation fails → Display errors, return to step 3
  **Exceptions**: Database error → Display error, allow retry

#### UC-006: View Analytics & KPIs

**Actor**: Traffic Engineer/Admin  
**Precondition**: Admin is logged in  
**Main Flow**:

1. Admin clicks "Analytics" tab
2. System queries metrics database
3. System calculates KPIs (avg density, incidents, MTTA/MTTR)
4. System displays dashboard with charts
5. Admin can filter by date range
6. Admin can export report (CSV/JSON)

**Postcondition**: Admin has performance insights  
**Alternative Flows**:

- 6a. Export to CSV → Generate file, trigger download
- 6b. Export to JSON → Generate file, trigger download
  **Exceptions**: No data available → Display "No data" message

#### UC-007: Request Emergency Preemption

**Actor**: Emergency Services  
**Precondition**: Emergency user is logged in  
**Main Flow**:

1. Emergency user selects route
2. Emergency user clicks "Request Preemption"
3. System validates route
4. System overrides signals along route
5. System provides green wave
6. System notifies operators
7. System logs preemption request
8. Emergency vehicle passes
9. System returns to normal operation

**Postcondition**: Emergency vehicle has priority passage  
**Alternative Flows**: None  
**Exceptions**: Invalid route → Display error, deny request

### 9.2 Glossary

| Term             | Definition                                                             |
| ---------------- | ---------------------------------------------------------------------- |
| Adaptive Control | Signal timing that adjusts based on real-time traffic conditions       |
| Approach         | Road segment leading to an intersection                                |
| Cycle            | Complete sequence of all signal phases at an intersection              |
| Detector         | Sensor that measures vehicle presence and count                        |
| Green Split      | Portion of cycle allocated to a specific phase                         |
| Incident         | Traffic event requiring operator attention (accident, breakdown, etc.) |
| Intersection     | Junction where two or more roads meet                                  |
| KPI              | Key Performance Indicator - metric for system performance              |
| MTTA             | Mean Time To Acknowledge - average time to acknowledge incidents       |
| MTTR             | Mean Time To Resolve - average time to resolve incidents               |
| Occupancy        | Percentage of time detector is occupied by vehicles                    |
| Phase            | Signal state configuration (which movements have green)                |
| Plan             | Set of phase timings for an intersection                               |
| Preemption       | Override of normal signal timing for emergency vehicles                |
| Queue            | Line of vehicles waiting at red signal                                 |
| WebSocket        | Protocol for real-time bidirectional communication                     |

### 9.3 Technology Stack Summary

**Backend**:

- Python 3.13.2
- Flask 3.0.0 (Web Framework)
- Flask-CORS 4.0.0 (CORS Support)
- OpenCV 4.12.0 (Computer Vision)
- NumPy 2.2.6 (Numerical Processing)
- NetworkX 3.2.1 (Graph Algorithms)

**Frontend**:

- React 18.2.0 (UI Framework)
- vis-network 9.1.9 (Graph Visualization)
- Tailwind CSS / Custom CSS (Styling)
- Axios (HTTP Client)
- Socket.io-client (WebSocket)

**Database**:

- SQLite (Development)
- PostgreSQL (Production)

**Development Tools**:

- Git (Version Control)
- VS Code (IDE)
- Chrome DevTools (Debugging)
- Postman (API Testing)

### 9.4 Revision History

| Version | Date       | Author           | Changes              |
| ------- | ---------- | ---------------- | -------------------- |
| 1.0     | 2025-10-31 | System Architect | Initial SRS document |

### 9.5 Approval

| Role            | Name               | Signature          | Date           |
| --------------- | ------------------ | ------------------ | -------------- |
| Project Manager | ******\_\_\_****** | ******\_\_\_****** | ****\_\_\_**** |
| Technical Lead  | ******\_\_\_****** | ******\_\_\_****** | ****\_\_\_**** |
| QA Lead         | ******\_\_\_****** | ******\_\_\_****** | ****\_\_\_**** |
| Stakeholder     | ******\_\_\_****** | ******\_\_\_****** | ****\_\_\_**** |

---

**End of Software Requirements Specification**
