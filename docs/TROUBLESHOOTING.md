# Troubleshooting Guide

This guide covers common issues encountered when running the CDM Ontologies Pipeline and their solutions.

## Common Issues

### Memory Issues

#### Out of Memory Errors

**Symptoms:**
- `java.lang.OutOfMemoryError: Java heap space`
- Process killed by system (OOM killer)
- Pipeline stops during merge or reasoning steps

**Solutions:**

1. **Increase Java heap size:**
```bash
# Check available memory
free -h

# Increase heap size (use 80% of available RAM)
export ROBOT_JAVA_ARGS="-Xmx64g"  # Adjust based on your system

# For very large systems
export ROBOT_JAVA_ARGS="-Xmx800g -XX:+UseG1GC"
```

2. **Use smaller dataset:**
```bash
# Switch to smaller configuration
ENV_FILE=.env.small make run-workflow

# Or test dataset
ENV_FILE=.env.test make run-workflow
```

3. **Optimize Java garbage collection:**
```bash
export ROBOT_JAVA_ARGS="-Xmx32g -XX:+UseG1GC -XX:+UseStringDeduplication -XX:MaxGCPauseMillis=200"
```

#### Memory Monitoring

```bash
# Monitor memory usage during pipeline
watch -n 10 'free -h && ps aux | grep -E "(robot|python)" | head -5'

# Check Java heap usage
jstat -gc -t $(pgrep java) 10s
```

### Network Issues

#### Download Timeouts

**Symptoms:**
- `requests.exceptions.Timeout`
- `Connection timed out`
- Slow or failed downloads

**Solutions:**

1. **Increase timeout:**
```bash
export TIMEOUT_SECONDS=60
export MAX_RETRIES=5
```

2. **Check network connectivity:**
```bash
# Test connectivity to ontology sources
curl -I http://purl.obolibrary.org/obo/bfo.owl
ping purl.obolibrary.org
```

3. **Use proxy if needed:**
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=https://proxy.example.com:8080
```

#### 404 Errors

**Symptoms:**
- `404 Client Error: Not Found`
- Specific ontologies fail to download

**Solutions:**

1. **Check URL status:**
```bash
# Test URL manually
curl -I http://purl.obolibrary.org/obo/problem.owl
```

2. **Update source file:**
```bash
# Remove problematic ontologies from source file
sed -i '/problem.owl/d' ontologies_source.txt
```

3. **Check version history:**
```bash
python version_manager.py history --ontology problem.owl
```

### File System Issues

#### Permission Denied

**Symptoms:**
- `Permission denied` errors
- Unable to create directories or files

**Solutions:**

1. **Check permissions:**
```bash
# Check current permissions
ls -la ontology_data_owl/
ls -la outputs/

# Fix permissions
chmod -R 755 ontology_data_owl/ outputs/
```

2. **Docker permission issues:**
```bash
# Ensure mounted volumes have correct permissions
sudo chown -R 1000:1000 ontology_data_owl/ outputs/

# Or use user mapping in docker-compose.yml
user: "${UID}:${GID}"
```

#### Disk Space Issues

**Symptoms:**
- `No space left on device`
- Pipeline stops during processing

**Solutions:**

1. **Check disk space:**
```bash
df -h
du -sh ontology_data_owl/ outputs/
```

2. **Clean up space:**
```bash
# Clean old outputs
make clean

# Clean old backups
python version_manager.py clean --keep 3

# Remove temporary files
rm -rf /tmp/pipeline_*
```

3. **Use different directories:**
```bash
# Move to larger disk
mv ontology_data_owl/ /large/disk/
ln -s /large/disk/ontology_data_owl ontology_data_owl
```

### Tool Issues

#### ROBOT Not Found

**Symptoms:**
- `robot: command not found`
- `java.lang.ClassNotFoundException`

**Solutions:**

1. **Use Docker (recommended):**
```bash
# ROBOT is pre-installed in container
make docker-build
make docker-test
```

2. **Install ROBOT manually:**
```bash
# Download ROBOT
cd /opt
sudo wget https://github.com/ontodev/robot/releases/download/v1.9.0/robot.jar

# Create wrapper script
sudo tee /usr/local/bin/robot > /dev/null <<EOF
#!/bin/bash
java -jar /opt/robot.jar "\$@"
EOF
sudo chmod +x /usr/local/bin/robot
```

#### relation-graph Not Found

**Symptoms:**
- `relation-graph: command not found`
- Missing relation-graph executable

**Solutions:**

1. **Use Docker (recommended):**
```bash
make docker-build
make docker-test
```

2. **Install relation-graph:**
```bash
cd /opt
sudo wget https://github.com/balhoff/relation-graph/releases/download/v2.3.1/relation-graph-2.3.1.tgz
sudo tar -xzf relation-graph-2.3.1.tgz
sudo ln -s /opt/relation-graph-2.3.1/bin/relation-graph /usr/local/bin/
```

### Pipeline Issues

#### Make Targets Fail

**Symptoms:**
- `make: *** No rule to make target`
- Make commands not working

**Solutions:**

1. **Check Makefile:**
```bash
# Verify Makefile exists
ls -la Makefile

# Check available targets
make help
```

2. **Check Python path:**
```bash
# Verify Python module structure
ls -la cdm_ontologies/
python -c "import cdm_ontologies; print('OK')"
```

3. **Run individual commands:**
```bash
# Run Python commands directly
python -m cdm_ontologies analyze-core
python scripts/analyze_core_ontologies.py
```

#### Version Tracking Issues

**Symptoms:**
- Version tracking not working
- Files always re-downloaded
- Checksum mismatches

**Solutions:**

1. **Check version files:**
```bash
# Check version registry
cat ontology_versions/ontology_versions.json

# Validate checksums
python version_manager.py validate
```

2. **Rebuild version registry:**
```bash
# Backup current registry
cp ontology_versions/ontology_versions.json ontology_versions.backup

# Rebuild from existing files
python version_manager.py rebuild-registry
```

3. **Reset version tracking:**
```bash
# Remove version tracking (will re-download everything)
rm -rf ontology_versions/
mkdir ontology_versions/
```

### Validation Failures

#### Validation Errors

**Symptoms:**
- `python test_validation.py` fails
- Missing expected output files

**Solutions:**

1. **Check pipeline logs:**
```bash
# View recent logs
tail -f logs/cdm_ontologies.log

# Check for errors
grep ERROR logs/cdm_ontologies.log
```

2. **Run validation step by step:**
```bash
# Validate individual steps
python test_validation.py 1
python test_validation.py 2
# ... continue for each step
```

3. **Check file existence:**
```bash
# Verify expected files exist
ls -la outputs/
ls -la ontology_data_owl/
```

#### Corrupt Files

**Symptoms:**
- Checksum validation failures
- Incomplete downloads
- Corrupted OWL files

**Solutions:**

1. **Re-download files:**
```bash
# Force re-download specific file
rm ontology_data_owl/problem.owl
python version_manager.py force-update problem.owl

# Or re-download all
make clean
make analyze-core
```

2. **Check file integrity:**
```bash
# Validate specific file
python version_manager.py validate --ontology problem.owl

# Check file size
ls -lh ontology_data_owl/problem.owl
```

## Docker Issues

### Container Build Issues

**Symptoms:**
- Docker build fails
- Missing dependencies in container

**Solutions:**

1. **Clear Docker cache:**
```bash
docker system prune -a
docker build --no-cache -t cdm-ontologies .
```

2. **Check Dockerfile:**
```bash
# Verify Dockerfile exists and is correct
cat Dockerfile
```

3. **Build step by step:**
```bash
# Build base image first
docker build --target base -t cdm-ontologies:base .
```

### Container Runtime Issues

**Symptoms:**
- Container exits immediately
- Permission issues in container

**Solutions:**

1. **Check container logs:**
```bash
docker logs cdm-ontologies-pipeline
```

2. **Run container interactively:**
```bash
docker run -it --rm cdm-ontologies:latest /bin/bash
```

3. **Check volume mounts:**
```bash
# Verify volumes are mounted correctly
docker run -it --rm -v $(pwd):/workspace cdm-ontologies:latest ls -la /workspace
```

## Kubernetes Issues

### Pod Issues

**Symptoms:**
- Pods not starting
- OutOfMemoryKilled status
- ImagePullBackOff

**Solutions:**

1. **Check pod status:**
```bash
kubectl get pods -n cdm-ontologies
kubectl describe pod <pod-name> -n cdm-ontologies
```

2. **Check resource limits:**
```bash
# Increase memory limits in job.yaml
resources:
  limits:
    memory: "1200Gi"
  requests:
    memory: "1000Gi"
```

3. **Check logs:**
```bash
kubectl logs <pod-name> -n cdm-ontologies
```

### Storage Issues

**Symptoms:**
- PVC not mounting
- Insufficient storage

**Solutions:**

1. **Check PVC status:**
```bash
kubectl get pvc -n cdm-ontologies
kubectl describe pvc ontology-data -n cdm-ontologies
```

2. **Increase storage size:**
```bash
# Edit PVC in pvc.yaml
spec:
  resources:
    requests:
      storage: 1000Gi
```

## Performance Issues

### Slow Processing

**Symptoms:**
- Pipeline takes too long
- High CPU usage
- Slow downloads

**Solutions:**

1. **Increase parallelism:**
```bash
export PARALLEL_DOWNLOADS=20
export BATCH_SIZE=200
```

2. **Optimize Java settings:**
```bash
export ROBOT_JAVA_ARGS="-Xmx32g -XX:+UseG1GC -XX:+UseStringDeduplication"
```

3. **Use faster storage:**
```bash
# Move to SSD
mv ontology_data_owl/ /fast/ssd/
ln -s /fast/ssd/ontology_data_owl ontology_data_owl
```

### Resource Monitoring

```bash
# Monitor system resources
htop

# Monitor disk I/O
iotop

# Monitor network
nethogs
```

## Debugging Tools

### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
export ENABLE_DETAILED_LOGGING=true
```

### Use Debugging Scripts

```bash
# Debug download issues
python scripts/debug_download.py --url http://example.com/ontology.owl

# Debug version tracking
python scripts/debug_versions.py --ontology bfo.owl

# Debug processing steps
python scripts/debug_processing.py --step analyze-core
```

### Manual Testing

```bash
# Test individual components
python -c "
from cdm_ontologies.downloader import EnhancedDownloader
downloader = EnhancedDownloader()
result = downloader.download('http://purl.obolibrary.org/obo/bfo.owl', 'test.owl')
print(result)
"
```

## Getting Help

### Log Files

Check these log files for detailed information:

- `logs/cdm_ontologies.log` - Main pipeline log
- `ontology_versions/download_history.log` - Download history
- `merge_memory.log` - Memory usage during merging

### Validation Tools

```bash
# Comprehensive validation
python test_validation.py all --verbose

# Version tracking validation
python test_validation.py version

# System requirements check
python scripts/check_requirements.py
```

### Community Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check `docs/` directory for detailed guides
- **Logs**: Always include relevant log files when reporting issues

### Useful Commands for Debugging

```bash
# System information
python --version
java -version
docker --version
kubectl version

# Environment information
env | grep -E "(ROBOT|JAVA|ONTOLOG)"
python -c "import sys; print(sys.path)"

# File information
ls -la ontology_data_owl/
ls -la outputs/
du -sh ontology_data_owl/ outputs/

# Process information
ps aux | grep -E "(robot|python)"
pgrep -f "cdm_ontologies"
```

This troubleshooting guide covers the most common issues encountered with the CDM Ontologies Pipeline. If you encounter an issue not covered here, please check the log files and report it as a GitHub issue with relevant details.