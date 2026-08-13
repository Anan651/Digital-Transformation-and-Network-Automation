import os
import re
import sqlite3
import argparse
import pandas as pd
from datetime import timedelta

# Define directory and file constants
LOG_DIR = 'logs'
OUTPUT_DIR = 'output'
DB_FILE = os.path.join(OUTPUT_DIR, 'network_events.db')
EVENTS_CSV = os.path.join(OUTPUT_DIR, 'events.csv')
RISK_CSV = os.path.join(OUTPUT_DIR, 'risk_report.csv')

# Regular expression patterns for parsing and classification
LOG_PATTERN = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(.*)$')
INTF_PATTERN = re.compile(r'Interface\s+(\S+)\s+changed\s+state\s+to\s+(up|down)', re.IGNORECASE)
BGP_PATTERN = re.compile(r'BGP\s+neighbor\s+(\S+)\s+(established|went down)', re.IGNORECASE)
CPU_PATTERN = re.compile(r'CPU\s+utilization\s+exceeded\s+(\d+)%', re.IGNORECASE)
THERMAL_PATTERN = re.compile(r'Temperature\s+sensor\s+(\S+)\s+exceeded\s+threshold', re.IGNORECASE)
SNMP_PATTERN = re.compile(r'SNMP\s+authentication\s+failure\s+from\s+(\S+)', re.IGNORECASE)

def get_recommendation(event, entity):
    """Generates a professional, actionable recommendation for network teams."""
    recommendations = {
        'Interface Flap': f"Investigate physical layer (cabling, SFP transceivers, line card) on interface {entity}. Check for duplex mismatches or hardware faults.",
        'BGP Instability': f"Check BGP configuration, peering status, and physical path stability for peer {entity}. Adjust BGP keepalive/hold timers if needed.",
        'CPU Spike': "Analyze active processes and device traffic. Consider throttling SNMP polling frequency, or scheduling telemetry during maintenance windows.",
        'SNMP Authentication Failure': f"Identify the source device at IP {entity}. Verify its configured SNMP community string or credentials. Block unauthorized polling using ACLs if necessary."
    }
    return recommendations.get(event, "Perform general health and hardware diagnostic checks.")

# --- 1. Log Parsing ---
def parse_logs():
    """Parses all log files in the logs directory into a structured Pandas DataFrame."""
    if not os.path.exists(LOG_DIR):
        print(f"⚠️ Error: Log directory '{LOG_DIR}' does not exist.")
        return pd.DataFrame()
    
    entries = []
    log_files = [f for f in os.listdir(LOG_DIR) if f.endswith('.txt')]
    
    if not log_files:
        print(f"⚠️ Warning: No .txt files found in '{LOG_DIR}' directory.")
        return pd.DataFrame()
        
    print(f"🔍 Found {len(log_files)} log files. Parsing raw log entries...")
    for filename in log_files:
        filepath = os.path.join(LOG_DIR, filename)
        with open(filepath, 'r') as file:
            for line_num, line in enumerate(file, 1):
                match = LOG_PATTERN.match(line.strip())
                if match:
                    timestamp, device, severity, message = match.groups()
                    entries.append({
                        'timestamp': pd.to_datetime(timestamp),
                        'device': device,
                        'severity': severity,
                        'message': message
                    })
                else:
                    if line.strip():
                        print(f"⚠️ Skipping unparseable line in {filename} (Line {line_num}): {line.strip()[:50]}")
                        
    return pd.DataFrame(entries)

# --- 2. Event Classification and Detail Extraction ---
def classify_and_extract(df):
    """Classifies log messages into distinct event categories and extracts relevant entities."""
    if df.empty:
        return df
    
    print("🏷️  Classifying network events...")
    categories, entities, values = [], [], []
    
    for message in df['message']:
        # Interface Changes
        m_intf = INTF_PATTERN.search(message)
        if m_intf:
            categories.append('Interface')
            entities.append(m_intf.group(1))
            values.append(m_intf.group(2).lower())
            continue
            
        # BGP neighbor events
        m_bgp = BGP_PATTERN.search(message)
        if m_bgp:
            categories.append('BGP')
            entities.append(m_bgp.group(1))
            values.append(m_bgp.group(2).lower())
            continue
            
        # CPU threshold exceeded
        m_cpu = CPU_PATTERN.search(message)
        if m_cpu:
            categories.append('CPU')
            entities.append('CPU')
            values.append(int(m_cpu.group(1)))
            continue
            
        # Thermal exceed events
        m_thermal = THERMAL_PATTERN.search(message)
        if m_thermal:
            categories.append('Thermal')
            entities.append(f"Sensor {m_thermal.group(1)}")
            values.append('exceeded')
            continue
            
        # SNMP authentication failure
        m_snmp = SNMP_PATTERN.search(message)
        if m_snmp:
            categories.append('SNMP')
            entities.append(m_snmp.group(1))
            values.append('failure')
            continue
            
        # Fallback category
        categories.append('Other')
        entities.append(None)
        values.append(None)
        
    df['event_category'] = categories
    df['target_entity'] = entities
    df['status_or_value'] = values
    return df

# --- 3. Risk Identification & Governance Rules ---
def analyze_risks(df):
    """Executes operational risk rules to generate the Risk Report."""
    if df.empty:
        return pd.DataFrame()
    
    print("📈 Analyzing operational risks based on governance rules...")
    risks = []
    df_sorted = df.sort_values(by='timestamp').copy()
    
    # ⚠️ Rule 1: Interface Flapping (down -> up within 5 mins, >=2 times/hour)
    intf_df = df_sorted[df_sorted['event_category'] == 'Interface'].copy()
    if not intf_df.empty:
        intf_df['prev_status'] = intf_df.groupby(['device', 'target_entity'])['status_or_value'].shift(1)
        intf_df['prev_timestamp'] = intf_df.groupby(['device', 'target_entity'])['timestamp'].shift(1)
        
        is_flap = (intf_df['status_or_value'] == 'up') & \
                  (intf_df['prev_status'] == 'down') & \
                  ((intf_df['timestamp'] - intf_df['prev_timestamp']).dt.total_seconds() <= 300)
                  
        flaps = intf_df[is_flap].copy()
        if not flaps.empty:
            flap_counts = flaps.groupby(['device', 'target_entity', pd.Grouper(key='timestamp', freq='h')]).size().reset_index(name='count')
            medium_risks = flap_counts[flap_counts['count'] >= 2]
            for _, r in medium_risks.iterrows():
                risks.append({
                    'Device': r['device'],
                    'Event': 'Interface Flap',
                    'Event_Detail': f"Interface {r['target_entity']} flapped {r['count']} times in 1 hour.",
                    'Count': int(r['count']),
                    'First_Seen': r['timestamp'],
                    'Risk_Level': 'Medium',
                    'Recommendation': get_recommendation('Interface Flap', r['target_entity'])
                })
                
    # ⚠️ Rule 2: BGP Instability (established -> down in 10 mins OR >=3 peer drops/day)
    bgp_df = df_sorted[df_sorted['event_category'] == 'BGP'].copy()
    if not bgp_df.empty:
        bgp_df['prev_status'] = bgp_df.groupby(['device', 'target_entity'])['status_or_value'].shift(1)
        bgp_df['prev_timestamp'] = bgp_df.groupby(['device', 'target_entity'])['timestamp'].shift(1)
        
        is_bgp_flap = (bgp_df['status_or_value'] == 'went down') & \
                      (bgp_df['prev_status'] == 'established') & \
                      ((bgp_df['timestamp'] - bgp_df['prev_timestamp']).dt.total_seconds() <= 600)
                      
        bgp_flaps = bgp_df[is_bgp_flap].copy()
        for _, r in bgp_flaps.iterrows():
            risks.append({
                'Device': r['device'],
                'Event': 'BGP Instability',
                'Event_Detail': f"BGP Peer {r['target_entity']} offline within 10 minutes of establishing.",
                'Count': 1,
                'First_Seen': r['timestamp'],
                'Risk_Level': 'High',
                'Recommendation': get_recommendation('BGP Instability', r['target_entity'])
            })
            
        bgp_downs = bgp_df[bgp_df['status_or_value'] == 'went down'].copy()
        if not bgp_downs.empty:
            daily_downs = bgp_downs.groupby(['device', pd.Grouper(key='timestamp', freq='D')]).size().reset_index(name='count')
            high_downs = daily_downs[daily_downs['count'] >= 3]
            for _, r in high_downs.iterrows():
                risks.append({
                    'Device': r['device'],
                    'Event': 'BGP Instability',
                    'Event_Detail': f"Device experienced {r['count']} peer disconnects in 1 day.",
                    'Count': int(r['count']),
                    'First_Seen': r['timestamp'],
                    'Risk_Level': 'High',
                    'Recommendation': get_recommendation('BGP Instability', 'multiple peers')
                })
                
    # ⚠️ Rule 3: CPU Spikes (>=95% Critical OR >=3 spikes >80% in 1 hour High)
    cpu_df = df_sorted[df_sorted['event_category'] == 'CPU'].copy()
    if not cpu_df.empty:
        critical_cpu = cpu_df[cpu_df['status_or_value'] >= 95].copy()
        for _, r in critical_cpu.iterrows():
            risks.append({
                'Device': r['device'],
                'Event': 'CPU Spike',
                'Event_Detail': f"Critical CPU usage reached {r['status_or_value']}% (exceeded 95% threshold).",
                'Count': 1,
                'First_Seen': r['timestamp'],
                'Risk_Level': 'Critical',
                'Recommendation': get_recommendation('CPU Spike', 'CPU')
            })
            
        cpu_spikes = cpu_df[cpu_df['status_or_value'] > 80].copy()
        if not cpu_spikes.empty:
            hourly_spikes = cpu_spikes.groupby(['device', pd.Grouper(key='timestamp', freq='h')]).size().reset_index(name='count')
            high_spikes = hourly_spikes[hourly_spikes['count'] >= 3]
            for _, r in high_spikes.iterrows():
                risks.append({
                    'Device': r['device'],
                    'Event': 'CPU Spike',
                    'Event_Detail': f"Device registered {r['count']} spikes (>80%) in 1 hour.",
                    'Count': int(r['count']),
                    'First_Seen': r['timestamp'],
                    'Risk_Level': 'High',
                    'Recommendation': get_recommendation('CPU Spike', 'CPU')
                })
                
    # ⚠️ Rule 4: SNMP Failures (Multiple failures from same source IP)
    snmp_df = df_sorted[df_sorted['event_category'] == 'SNMP'].copy()
    if not snmp_df.empty:
        snmp_counts = snmp_df.groupby(['device', 'target_entity']).size().reset_index(name='count')
        repeated_failures = snmp_counts[snmp_counts['count'] > 1]
        for _, r in repeated_failures.iterrows():
            first_seen = snmp_df[(snmp_df['device'] == r['device']) & (snmp_df['target_entity'] == r['target_entity'])]['timestamp'].min()
            risks.append({
                'Device': r['device'],
                'Event': 'SNMP Authentication Failure',
                'Event_Detail': f"Repeated SNMP authorization failures ({r['count']}) from IP {r['target_entity']}.",
                'Count': int(r['count']),
                'First_Seen': first_seen,
                'Risk_Level': 'High',
                'Recommendation': get_recommendation('SNMP Authentication Failure', r['target_entity'])
            })
            
    return pd.DataFrame(risks)

# --- 4. Database Integration & Output Management ---
def save_outputs(events_df, risk_df):
    """Saves parsed datasets to clean CSV reports and updates the SQLite DB."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # Write professional reports to CSV
    events_df.to_csv(EVENTS_CSV, index=False)
    print(f"💾 Saved events report to: {EVENTS_CSV}")
    
    if not risk_df.empty:
        risk_df.to_csv(RISK_CSV, index=False)
        print(f"💾 Saved risk assessment report to: {RISK_CSV}")
    else:
        pd.DataFrame(columns=['Device', 'Event', 'Event_Detail', 'Count', 'First_Seen', 'Risk_Level', 'Recommendation']).to_csv(RISK_CSV, index=False)
        print("💾 Saved risk assessment report (Empty/No risks found).")
        
    # Standardize data tables inside SQL Database
    conn = sqlite3.connect(DB_FILE)
    try:
        events_df.to_sql('events', conn, if_exists='replace', index=False)
        if not risk_df.empty:
            risk_df.to_sql('risk_summary', conn, if_exists='replace', index=False)
        print(f"🛢️  Successfully built/updated SQLite Database: {DB_FILE}")
    except Exception as e:
        print(f"❌ Error writing to database: {e}")
    finally:
        conn.close()

# --- Main Runtime Logic ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vodafone Assessment: Advanced Network Log Analyzer")
    parser.add_argument('--device', help='Filter risk outputs displayed in the CLI by device name')
    parser.add_argument('--risk-level', help='Filter risk outputs displayed in the CLI by risk level (Critical/High/Medium)')
    args = parser.parse_args()
    
    # Run pipeline
    raw_df = parse_logs()
    
    if not raw_df.empty:
        classified_df = classify_and_extract(raw_df)
        final_risk_df = analyze_risks(classified_df)
        save_outputs(classified_df, final_risk_df)
        
        # Output filtering for command-line convenience
        cli_display_df = final_risk_df.copy()
        if not cli_display_df.empty:
            if args.device:
                cli_display_df = cli_display_df[cli_display_df['Device'] == args.device]
            if args.risk_level:
                cli_display_df = cli_display_df[cli_display_df['Risk_Level'] == args.risk_level]
                
            print("\n" + "="*50 + "\n🔥 IDENTIFIED NETWORK RISKS SUMMARY\n" + "="*50)
            if not cli_display_df.empty:
                print(cli_display_df.to_markdown(index=False))
            else:
                print("No active risks match your command-line filters.")
        else:
            print("\n✅ Clean Bill of Health: No risks were identified.")
