# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in BlenderMCP, please report it by emailing the maintainers or opening a private security advisory on GitHub. **Do not open public issues for security vulnerabilities.**

## Security Best Practices

### For Users

#### 1. Code Execution Risks

The `execute_blender_code` feature is powerful but potentially dangerous:

- ⚠️ **Only use with trusted AI models and prompts**
- Review generated code when possible before execution
- Always save your work before executing code
- Consider disabling this feature in shared/production environments

#### 2. API Key Management

Protect your API keys:

- **Never commit API keys to version control**
- Store keys in the Blender addon UI or use environment variables
- **Warning**: Keys entered in Blender UI may be saved in .blend files
- Don't share .blend files that contain API keys
- Rotate keys regularly
- Use different keys for development and production

#### 3. Network Security

- The Blender socket server binds to `localhost:9876` by default
- This is safe for single-user development
- For production use, consider additional authentication
- Use Docker isolation when running in untrusted environments

#### 4. File System Access

The tool has access to your file system through Blender's Python API:

- Only download assets from trusted sources
- Review file paths before large batch operations
- Keep the workspace isolated from sensitive data

#### 5. Privacy & Telemetry

Anonymous telemetry is enabled by default but respects your privacy:

- **No personal data collected**
- **No prompt text collected** (unless explicitly enabled)
- Only usage patterns and anonymous UUIDs

To disable telemetry:
```bash
export DISABLE_TELEMETRY=true
```

### For Developers

#### 1. Dependency Management

- Regularly update dependencies
- Use `pip-audit` or similar tools to scan for vulnerabilities
- Pin dependency versions in production

#### 2. Input Validation

When contributing:

- Validate all user inputs
- Sanitize file paths (prevent path traversal)
- Validate URLs before downloads
- Use allowlists for external domains

#### 3. Secure Configuration

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Provide `.env.example` without actual credentials
- Document all security-relevant configuration options

#### 4. Code Review

- All code execution paths should be reviewed
- Pay special attention to:
  - File system operations
  - Network requests
  - Code execution (exec, eval)
  - Subprocess calls

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.4.x   | :white_check_mark: |
| < 1.4   | :x:                |

## Known Security Considerations

### 1. Arbitrary Code Execution
- **Severity**: High
- **Status**: By design - feature requires this capability
- **Mitigation**: User education, warnings in documentation

### 2. No Socket Authentication
- **Severity**: Medium
- **Status**: Known limitation for ease of use
- **Mitigation**: Binds to localhost only, recommended for development use

### 3. API Keys in Blender Properties
- **Severity**: Medium
- **Status**: Blender limitation - properties may be saved in files
- **Mitigation**: User warnings, consider implementing encrypted storage

### 4. External Asset Downloads
- **Severity**: Low
- **Status**: Required for functionality
- **Mitigation**: Only from trusted sources (PolyHaven, Sketchfab)

## Security Checklist for Users

Before deploying to production:

- [ ] Telemetry disabled or reviewed
- [ ] API keys stored securely (not in .blend files)
- [ ] Code execution feature understood and reviewed
- [ ] Running in isolated environment (Docker recommended)
- [ ] Network access restricted to necessary services
- [ ] Blender files with embedded keys not shared
- [ ] Regular backups of important work
- [ ] Dependencies up to date

## Incident Response

If you believe you've been affected by a security issue:

1. Stop using the affected feature
2. Rotate any potentially exposed API keys
3. Report the issue through appropriate channels
4. Review recent activity for suspicious behavior
5. Update to the latest version when a fix is available

## Updates

Security policies and best practices will be updated as the project evolves. Check this document regularly for updates.

---

Last updated: December 2025
