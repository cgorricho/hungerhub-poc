# 🗄️ Database Connection Information

**Last Updated**: 2025-08-07  
**Status**: ✅ RECEIVED - Ready for Oracle Development  

## 📊 Available Databases

### **Choice Sandbox Database**
**Purpose**: Donations, Choice Program Data, Bidding System  
**Connection Details**:
- **Host**: 52.43.135.66
- **Port**: 1521
- **Service Name**: staging
- **Database Name**: A2H817P1
- **User ID**: rwtxn_46
- **Password**: rwtxn_46

**Expected Tables** (based on sample data):
- `AMX_DONATION_HEADER` - Donation header records
- `AMX_DONATION_LINES` - Donation line items  
- `AMX_OFFER_HEADER` - Offer header records
- `AMX_OFFER_LINES` - Offer line items
- `CHOICE_DOCUMENTHEADER` - Choice program document headers
- `CHOICE_DOCUMENTLINES` - Choice program document lines
- `ACBIDS_ARCHIVE` - Auction/bidding data
- `RW_ORG` - Organizations (shared)
- `RW_USER` - Users (shared)

### **AgencyExpress Sandbox Database**
**Purpose**: Agency Operations, Food Pantry Orders, Distribution  
**Connection Details**:
- **Host**: 52.43.135.66
- **Port**: 1521
- **Service Name**: staging
- **Database Name**: AETRAN
- **User ID**: tran_user
- **Password**: tran_user

**Expected Tables** (based on sample data):
- `AE_DOCUMENTHEADER` - Agency Express document headers
- `AE_DOCUMENTLINE` - Agency Express document lines
- `RW_ORG` - Organizations (shared)
- `RW_USER` - Users (shared)

## 🎯 Data Architecture Notes

### **Shared Tables**:
- `RW_ORG` and `RW_USER` appear in both databases
- May contain overlapping or complementary data
- Need to analyze for data consistency and relationships

### **Data Flow Strategy**:
1. **Choice Database** → Donation analytics, Choice program insights
2. **Agency Database** → Agency operations, fulfillment metrics  
3. **Combined Analysis** → Integrated dashboard with cross-database insights

## ✅ Next Steps
- Test connectivity to both databases
- Explore table structures and data volumes
- Identify key relationships between databases
- Begin data extraction from priority tables

---
**Security Note**: Credentials stored in `config/.env` with restricted permissions (600)
