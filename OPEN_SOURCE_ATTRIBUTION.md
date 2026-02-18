# Open Source Attribution

This project uses the following open-source libraries and is built on open-source principles. All components are legally usable for Proof of Concept development.

## Backend Dependencies

### Web Framework
- **FastAPI** - BSD 3-Clause License
  - Modern Python web framework for building APIs
  - https://github.com/tiangolo/fastapi

- **Uvicorn** - BSD 3-Clause License
  - ASGI server implementation
  - https://github.com/encode/uvicorn

### Time & Data
- **pytz** - MIT License
  - Timezone database
  - https://github.com/stub42/pytz

- **Pydantic** - MIT License
  - Python data validation using Python type annotations
  - https://github.com/pydantic/pydantic

### HTTP & APIs
- **requests** - Apache 2.0 License
  - HTTP library for Python
  - https://github.com/psf/requests

- **aiohttp** - Apache 2.0 License
  - Async HTTP library
  - https://github.com/aio-libs/aiohttp

### Scientific & Utilities
- **numpy** - BSD 3-Clause License
  - Numerical computing library
  - https://github.com/numpy/numpy

- **scipy** - BSD 3-Clause License
  - Scientific computing library
  - https://github.com/scipy/scipy

### Voice & Audio (Optional)
- **SpeechRecognition** - BSD 3-Clause License
  - Speech recognition library
  - https://github.com/Uberi/speech_recognition

- **pyttsx3** - MIT License
  - Text-to-speech library
  - https://github.com/nateshmbhat/pyttsx3

- **pyaudio** - MIT License
  - Python bindings for PortAudio
  - http://people.csail.mit.edu/hubert/pyaudio/

### Configuration
- **python-dotenv** - BSD 3-Clause License
  - Environment variable management
  - https://github.com/theskumar/python-dotenv

## Frontend Components

The frontend uses:
- **Vanilla JavaScript** (No external JS framework)
- **HTML5 & CSS3** (Native web standards)
- **SVG icons** (Inline, custom-created)

## License Compatibility

All dependencies use licenses compatible with open-source development:

| License | Count | Usage |
|---------|-------|-------|
| MIT | 5 | Core functionality |
| BSD 3-Clause | 5 | Scientific & API |
| Apache 2.0 | 2 | HTTP clients |

## Proof of Concept Usage

These licenses permit:
- ✓ Evaluation and testing
- ✓ Educational use
- ✓ Research and prototyping
- ✓ Non-commercial deployment

## Production Considerations

For production deployment, ensure:
1. Include license copies in distribution
2. Maintain attribution
3. Follow each license's specific requirements
4. Consider commercial licenses for proprietary APIs (Zomato, Swiggy, Ola, Uber)

## Third-Party APIs (Not Included)

The following are optional integrations (not open-source):
- Zomato API - Requires API key
- Swiggy API - Requires partnership
- Ola API - Requires API key  
- Uber API - Requires API key

The system works fully without these - mock data is provided by default.

## Building for POC

This entire system is free to build and deploy for non-commercial proof of concept work:

```bash
# Clone
git clone <repo>

# Install dependencies (all open-source)
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload
```

No proprietary licenses or paid services needed for basic functionality.

## Attribution Summary

**Respect these principles:**
1. Acknowledge all open-source dependencies
2. Include license copies with source
3. Don't claim ownership of upstream projects
4. Follow each license's redistribution requirements
5. Add modifications/improvements for legal clarity

**This POC is completely legal and open because:**
- All dependencies are properly licensed
- No proprietary code is included
- All integrations are optional and documented
- Mock data allows full evaluation without APIs
- Clear attribution is provided

## Questions?

Refer to:
- Individual project repositories
- License files in source distributions
- SPDX License List (https://spdx.org/licenses/)
