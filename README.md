# AEGIS AI SmartEdu - Simplified Version

This is a cleaned, easier-to-learn version of your project.

## Main flow
1. User registers and logs in.
2. User uploads one class timetable and one or more module timetable files.
3. Files are saved in `uploads/timetables/user_<id>/`.
4. Metadata and preferences are saved in SQLite.
5. The extraction pipeline reads uploaded files, parses them into text, sends the text to the extraction agent, and returns structured JSON.

## Important folders
- `app.py` - Flask entry point
- `database.py` - SQLite helper
- `backend/routes/upload_routes.py` - upload page and save logic
- `backend/services/file_parsing_service.py` - PDF/CSV/XLSX to text
- `backend/agents/extraction_agent.py` - AI extraction logic
- `backend/services/extraction_pipeline_service.py` - full extraction flow

## Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

## Test the extraction pipeline
```bash
set USE_MOCK_LLM=1
python test_extraction_agent.py
```

Use mock mode first if your AWS Bedrock keys are not ready.
