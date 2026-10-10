# MoveInSync FDE Case Study — Makefile

.PHONY: install pipeline collect clean classify analyze dashboard report test

install:
	pip install -r requirements.txt
	python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')" 2>/dev/null || true

collect:
	python src/collect_reviews.py --app-id com.moveinsync.ets --lang en --country in --count 5000

clean:
	python src/clean_reviews.py

classify:
	python src/classify_reviews.py

analyze:
	python src/analyze_reviews.py

dashboard-data:
	python src/build_dashboard_data.py

pipeline: collect clean classify analyze dashboard-data
	@echo "✅ Full pipeline complete."

dashboard:
	streamlit run app/streamlit_app.py --server.port 8501

report:
	python src/generate_report.py

test:
	python -m pytest tests/ -v

check-data:
	@python -c "import pandas as pd; df=pd.read_csv('data/raw/google_play_reviews.csv'); print(f'Raw: {len(df)} reviews'); df2=pd.read_csv('data/processed/google_play_reviews_clean.csv'); print(f'Clean: {len(df2)} reviews')"
