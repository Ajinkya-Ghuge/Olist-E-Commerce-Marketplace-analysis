@echo off
echo ========================================
echo Olist E-Commerce Analytics Pipeline
echo ========================================
echo.

echo [1/5] Running Data Profiling...
python analysis/01_simple_data_profiling.py
echo [SUCCESS] Data profiling complete
echo.

echo [2/5] Running Data Cleaning...
python analysis/02_simple_data_cleaning.py
echo [SUCCESS] Data cleaning complete
echo.

echo [3/5] Running Business Analysis...
python analysis/03_simple_business_analysis.py
echo [SUCCESS] Business analysis complete
echo.

echo [4/5] Running SQL Analysis...
python analysis/04_sql_analysis.py
echo [SUCCESS] SQL analysis complete
echo.

echo [5/5] Generating Visualizations...
python analysis/05_visualizations.py
echo [SUCCESS] Visualizations generated
echo.

echo ========================================
echo All Done!
echo ========================================
echo.
echo Next Steps:
echo 1. Open dashboard.html in your browser
echo 2. Check reports/business_insights.txt
echo 3. View charts in reports/charts/
echo.
pause
