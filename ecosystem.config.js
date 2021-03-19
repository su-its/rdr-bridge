module.exports = {
  apps : [{
    name: 'rdr-bridge',
    script: 'main.py',
    interpreter: 'python3',
    watch: false,
    restart_delay: 1000,
    log_date_format: 'YYYY-MM-DD HH:mm Z',
    merge_logs: true
  }]
}
