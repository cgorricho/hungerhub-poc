# Database Connection Guide
**HungerHub POC - Technical Documentation**

---

## 🔍 Connection Detection & Fallback Strategy

### **Intelligent Connection Mode Detection**

The Smart ETL Pipeline automatically detects the optimal data connection approach:

```python
def detect_connection_mode(self) -> str:
    """
    Intelligently detects whether to use real or mock data
    
    Process:
    1. Test network connectivity to Azure SQL servers
    2. Attempt database authentication with multiple methods
    3. Fall back to enhanced mock data if connections fail
    
    Returns:
        'REAL': Live database connections established
        'MOCK': Using realistic mock data for development
    """
```

### **Authentication Methods Tested**

The system attempts multiple authentication approaches in order:

1. **ActiveDirectoryDefault** *(Primary)*
   - Uses Azure managed identity
   - Best for production Azure environments
   - Connection String: `Authentication=ActiveDirectoryDefault`

2. **ActiveDirectoryIntegrated** *(Secondary)*
   - Uses integrated Windows authentication
   - Good for domain-joined machines
   - Connection String: `Trusted_Connection=yes`

3. **ActiveDirectoryManagedIdentity** *(Tertiary)*
   - Uses Azure Managed Service Identity
   - For Azure VM deployments
   - Connection String: `Authentication=ActiveDirectoryMsi`

4. **SqlServerAuthentication** *(If Credentials Available)*
   - Traditional username/password
   - Requires explicit credentials
   - Connection String: `UID={username};PWD={password}`

### **Network Connectivity Testing**

Before attempting database connections, the system tests:

```python
def _test_network_connectivity(self, server: str, port: int = 1433) -> bool:
    """
    Tests basic TCP connectivity to SQL Server
    
    Servers Tested:
    - choice-sql-server.database.windows.net:1433
    - agencyexpress-sql-server.database.windows.net:1433
    
    Returns:
        True: Network path accessible
        False: Server unreachable (firewall, DNS, etc.)
    """
```

---

## 🔧 Configuration Management

### **Environment Variables**

The system looks for database configuration in this priority order:

1. **Primary Variables:**
   ```bash
   CHOICE_DB_SERVER=choice-sql-server.database.windows.net
   CHOICE_DB_NAME=Choice
   AGENCY_DB_SERVER=agencyexpress-sql-server.database.windows.net
   AGENCY_DB_NAME=AgencyExpress
   ```

2. **Authentication Variables:**
   ```bash
   DB_AUTH_METHOD=ActiveDirectoryDefault
   DB_USERNAME=  # Optional
   DB_PASSWORD=  # Optional
   ```

3. **Alternative Naming (Compatibility):**
   ```bash
   AZURE_SQL_SERVER=
   AZURE_SQL_DATABASE=
   AZURE_SQL_USERNAME=
   AZURE_SQL_PASSWORD=
   ```

### **Connection String Building**

Connection strings are built dynamically based on available configuration:

```python
# Example: ActiveDirectoryDefault
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Authentication=ActiveDirectoryDefault;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)
```

---

## 🚨 Troubleshooting Guide

### **Common Connection Issues**

#### Issue 1: DNS Resolution Failed
```
Error: [Errno -2] Name or service not known
```
**Causes:**
- Server names may be placeholder/fictional
- Network firewall blocking DNS queries
- VPN required for access

**Solutions:**
1. Verify server names are correct
2. Test DNS resolution: `nslookup choice-sql-server.database.windows.net`
3. Check network connectivity and firewall rules

#### Issue 2: Authentication Failed
```
Error: Invalid value specified for connection string attribute 'Authentication'
```
**Causes:**
- ODBC driver version incompatibility
- Authentication method not supported
- Missing Azure credentials

**Solutions:**
1. Try alternative authentication methods
2. Verify ODBC driver version: `odbcinst -q -d`
3. Check Azure identity configuration

#### Issue 3: Connection Timeout
```
Error: Connection timeout expired
```
**Causes:**
- Network latency issues
- Server overloaded
- Firewall blocking connections

**Solutions:**
1. Increase connection timeout
2. Test network path: `telnet server 1433`
3. Check Azure SQL firewall rules

### **Testing Connection Methods**

Use the comprehensive database test script:

```bash
python3 scripts/comprehensive_db_test.py
```

This script will:
- Test network connectivity
- Try all authentication methods
- Report detailed results
- Save test logs for analysis

---

## 📊 Mock Data Fallback System

### **When Mock Data is Used**

Mock data automatically activates when:
1. Network connectivity fails to database servers
2. All authentication methods fail
3. Database access is denied

### **Mock Data Quality**

The enhanced mock data system provides:
- **Realistic Distributions:** Uses Poisson for household sizes, normal for food amounts
- **Temporal Patterns:** Realistic service dates and frequencies
- **Geographic Diversity:** Multiple states and cities
- **Data Relationships:** Consistent foreign key relationships
- **Validation Challenges:** Some edge cases to test validation logic

### **Mock vs Real Data Comparison**

| Aspect | Mock Data | Real Data |
|--------|-----------|-----------|
| **Volume** | 35 people, 219 services | Actual database size |
| **Quality** | 100% clean, validated | May have real-world issues |
| **Patterns** | Algorithmically generated | Reflects actual usage |
| **Testing** | Perfect for development | Required for production |
| **Performance** | Instant generation | Depends on network/DB |

---

## 🔄 Production Deployment Guide

### **Establishing Real Connections**

For production deployment:

1. **Verify Network Access:**
   ```bash
   # Test network connectivity
   telnet choice-sql-server.database.windows.net 1433
   telnet agencyexpress-sql-server.database.windows.net 1433
   ```

2. **Configure Authentication:**
   - For Azure VMs: Use Managed Identity
   - For on-premises: Use Service Principal
   - For development: Use Azure CLI login

3. **Set Environment Variables:**
   ```bash
   export CHOICE_DB_SERVER="actual-server.database.windows.net"
   export CHOICE_DB_NAME="ActualDatabaseName"
   # ... additional configuration
   ```

4. **Test Connections:**
   ```bash
   python3 scripts/comprehensive_db_test.py
   ```

5. **Run ETL Pipeline:**
   ```bash
   python3 src/smart_etl_pipeline.py
   ```

### **Monitoring Connection Health**

The system provides connection monitoring through:
- Automated connection testing
- Fallback mode detection
- Connection performance metrics
- Error logging and alerting

---

## 📋 Connection Status Reporting

### **Connection Test Results**

The comprehensive test script generates detailed reports:

```json
{
  "network_tests": {
    "choice_server": true/false,
    "agency_server": true/false
  },
  "choice_auth": {
    "ActiveDirectoryDefault": {
      "status": "SUCCESS/FAILED",
      "connection_string": "...",
      "test_time": "2025-08-07T19:05:52"
    }
  },
  "summary": {
    "successful_connections": 2,
    "recommended_method": "ActiveDirectoryDefault"
  }
}
```

### **ETL Pipeline Connection Reporting**

Each ETL run reports its connection mode:

```json
{
  "connection_mode": "REAL/MOCK",
  "etl_timestamp": "2025-08-07T19:09:50",
  "validation_score": 100.0,
  "total_records": 219
}
```

---

**Last Updated:** August 7, 2025  
**Version:** Enhanced v2.0  
**Status:** Production Ready with Intelligent Fallback
