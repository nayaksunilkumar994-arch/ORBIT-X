function MissionControl() {
    return (
      <main className="mission-control">
        <header className="mission-header">
          <div>
            <p className="eyebrow">ORBIT-X // SPACE CYBER DEFENSE</p>
            <h1>Mission Control</h1>
            <p className="mission-subtitle">
              Autonomous Cyber Defense & Digital Twin for Space Systems
            </p>
          </div>
  
          <div className="system-status">
            <span className="status-dot" />
            SYSTEM OPERATIONAL
          </div>
        </header>
  
        <section className="mission-overview">
          <div className="overview-card">
            <span>MISSION</span>
            <strong>ORBIT-X-01</strong>
          </div>
  
          <div className="overview-card">
            <span>SPACECRAFT</span>
            <strong>ORBIT-X SAT-01</strong>
          </div>
  
          <div className="overview-card">
            <span>MISSION PHASE</span>
            <strong>NOMINAL</strong>
          </div>
  
          <div className="overview-card">
            <span>THREAT LEVEL</span>
            <strong>LOW</strong>
          </div>
        </section>
  
        <section className="dashboard-grid">
          <div className="dashboard-card spacecraft-card">
            <div className="card-header">
              <h2>Spacecraft Digital Twin</h2>
              <span>LIVE SIMULATION</span>
            </div>
  
            <div className="spacecraft-placeholder">
              <div className="spacecraft-core">
                ORBIT-X
              </div>
  
              <div className="subsystem power">
                POWER
              </div>
  
              <div className="subsystem thermal">
                THERMAL
              </div>
  
              <div className="subsystem comm">
                COMM
              </div>
  
              <div className="subsystem navigation">
                NAV
              </div>
            </div>
          </div>
  
          <div className="dashboard-card telemetry-card">
            <div className="card-header">
              <h2>Telemetry</h2>
              <span>LIVE</span>
            </div>
  
            <div className="telemetry-grid">
              <div>
                <span>CPU</span>
                <strong>42%</strong>
              </div>
  
              <div>
                <span>POWER</span>
                <strong>87%</strong>
              </div>
  
              <div>
                <span>TEMPERATURE</span>
                <strong>24.8°C</strong>
              </div>
  
              <div>
                <span>LINK</span>
                <strong>98%</strong>
              </div>
            </div>
          </div>
  
          <div className="dashboard-card threat-card">
            <div className="card-header">
              <h2>Threat Detection</h2>
              <span>MONITORING</span>
            </div>
  
            <div className="threat-state">
              <strong>NO ACTIVE THREATS</strong>
              <p>
                Detection engine is monitoring spacecraft telemetry and security
                events.
              </p>
            </div>
          </div>
  
          <div className="dashboard-card response-card">
            <div className="card-header">
              <h2>Autonomous Response</h2>
              <span>READY</span>
            </div>
  
            <div className="response-state">
              <strong>DEFENSE ENGINE ARMED</strong>
              <p>
                Safe simulated response actions are available when an incident is
                detected.
              </p>
            </div>
          </div>
        </section>
      </main>
    )
  }
  
  export default MissionControl