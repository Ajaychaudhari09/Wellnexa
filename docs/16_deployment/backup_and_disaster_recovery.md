# WellNexa AI — Backup & Disaster Recovery Plan

## 1. Automated PostgreSQL Backup Schedule
```bash
# Automated daily backup cron script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
docker exec -t wellnexa-postgres pg_dump -U wellnexa_user -d wellnexa_db -F c -b -v -f "${BACKUP_DIR}/wellnexa_${TIMESTAMP}.dump"

# Retain 30 days of rolling backups
find ${BACKUP_DIR} -type f -name "*.dump" -mtime +30 -exec rm {} \;
```

## 2. Disaster Recovery & Database Restoration
```bash
# Restore from backup snapshot
docker exec -i wellnexa-postgres pg_restore -U wellnexa_user -d wellnexa_db -v -c "/backups/postgres/wellnexa_20260827_000000.dump"
```

## 3. Recovery Time & Point Objectives
- **RTO (Recovery Time Objective)**: $< 15\text{ minutes}$.
- **RPO (Recovery Point Objective)**: $< 24\text{ hours}$ (daily snapshot + WAL archiving).
