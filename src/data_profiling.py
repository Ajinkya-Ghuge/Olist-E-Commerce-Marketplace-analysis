"""
Olist Analytics Pro - Data Profiling Module

This module profiles CSV files to understand their structure, quality, and relationships.
It generates comprehensive reports about row counts, columns, data types, missing values,
duplicates, and potential keys.

Author: Portfolio Project
Date: 2026-10-20
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class DataProfiler:
    """
    A class to profile CSV datasets and generate quality reports.
    
    Attributes:
        data_dir (Path): Directory containing CSV files
        output_dir (Path): Directory for saving reports
        profile_results (dict): Storage for profiling results
    """
    
    def __init__(self, data_dir: str, output_dir: str):
        """
        Initialize the DataProfiler.
        
        Args:
            data_dir: Path to directory containing CSV files
            output_dir: Path to directory for saving reports
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.profile_results = {}
        
    def discover_olist_files(self) -> list:
        """
        Discover all Olist-related CSV files in the data directory.
        
        Returns:
            List of Path objects for Olist CSV files
        """
        # Look for files with 'olist' or 'product_category' in name
        all_files = list(self.data_dir.glob('*.csv'))
        olist_files = [
            f for f in all_files 
            if 'olist' in f.name.lower() or 'product_category' in f.name.lower()
        ]
        return sorted(olist_files)
    
    def profile_file(self, file_path: Path, chunk_size: int = None) -> dict:
        """
        Profile a single CSV file and return comprehensive statistics.
        
        Args:
            file_path: Path to the CSV file
            chunk_size: If specified, read file in chunks (for large files)
            
        Returns:
            Dictionary containing profiling results
        """
        print(f"\n{'='*80}")
        print(f"PROFILING: {file_path.name}")
        print(f"{'='*80}")
        
        profile = {
            'filename': file_path.name,
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
            'profiling_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # For large files (>100MB), use chunking
            if profile['file_size_mb'] > 100 and chunk_size:
                profile.update(self._profile_large_file(file_path, chunk_size))
            else:
                df = pd.read_csv(file_path)
                profile.update(self._profile_dataframe(df, file_path.name))
            
            return profile
            
        except Exception as e:
            profile['error'] = str(e)
            print(f"[ERROR] Failed to profile {file_path.name}: {e}")
            return profile
    
    def _profile_large_file(self, file_path: Path, chunk_size: int) -> dict:
        """
        Profile large CSV files using chunked reading with Pandas aggregations.
        
        This method demonstrates:
        - Chunked processing for memory efficiency
        - Vectorized aggregations across chunks
        - NumPy array operations for statistics
        
        Args:
            file_path: Path to the CSV file
            chunk_size: Number of rows per chunk
            
        Returns:
            Dictionary with profile statistics
        """
        print(f"[INFO] Large file detected - using chunked processing...")
        
        # First chunk to get column info
        first_chunk = pd.read_csv(file_path, nrows=chunk_size)
        
        profile = {
            'columns': first_chunk.columns.tolist(),
            'column_count': len(first_chunk.columns),
            'data_types': first_chunk.dtypes.astype(str).to_dict(),
            'note': f'Chunked processing used (chunk_size={chunk_size})'
        }
        
        # Initialize aggregators using NumPy arrays for efficiency
        total_rows = 0
        missing_counts = pd.Series(0, index=first_chunk.columns)
        duplicate_count = 0
        
        # Use generator for memory efficiency
        chunk_reader = pd.read_csv(file_path, chunksize=chunk_size)
        
        print("Processing chunks...")
        for i, chunk in enumerate(chunk_reader, 1):
            # Vectorized operations on each chunk
            total_rows += len(chunk)
            missing_counts += chunk.isnull().sum()  # Vectorized missing value count
            duplicate_count += chunk.duplicated().sum()  # Vectorized duplicate detection
            
            if i % 5 == 0:  # Progress indicator
                print(f"   Processed {total_rows:,} rows...")
        
        profile['row_count'] = total_rows
        profile['duplicate_rows'] = int(duplicate_count)
        profile['duplicate_row_percentage'] = round(duplicate_count / total_rows * 100, 2)
        
        # Calculate missing value percentages using vectorized operations
        profile['missing_values'] = missing_counts.to_dict()
        profile['missing_percentages'] = (missing_counts / total_rows * 100).round(2).to_dict()
        
        # Sample data
        profile['sample_data'] = first_chunk.head(3).to_dict()
        
        print(f"[SUCCESS] Total rows: {total_rows:,}")
        print(f"[SUCCESS] Columns: {profile['column_count']}")
        print(f"[INFO] Duplicates: {duplicate_count:,} ({profile['duplicate_row_percentage']}%)")
        
        return profile
    
    def _profile_dataframe(self, df: pd.DataFrame, filename: str) -> dict:
        """
        Generate comprehensive profile for a loaded DataFrame using Pandas vectorized operations.
        
        This method demonstrates advanced Pandas techniques:
        - Vectorized operations instead of loops
        - Boolean masking for filtering
        - Method chaining for efficiency
        - Built-in aggregation functions
        
        Args:
            df: Pandas DataFrame
            filename: Name of the source file
            
        Returns:
            Dictionary with detailed profile statistics
        """
        profile = {}
        
        # ============================================================
        # BASIC SHAPE ANALYSIS - Using Pandas attributes
        # ============================================================
        profile['row_count'] = len(df)
        profile['column_count'] = len(df.columns)
        profile['columns'] = df.columns.tolist()
        profile['memory_usage_mb'] = round(df.memory_usage(deep=True).sum() / (1024**2), 2)
        
        print(f"[DATA] Rows: {profile['row_count']:,}")
        print(f"[DATA] Columns: {profile['column_count']}")
        print(f"[DATA] Memory Usage: {profile['memory_usage_mb']} MB")
        
        # ============================================================
        # DATA TYPES - Vectorized type detection
        # ============================================================
        profile['data_types'] = df.dtypes.astype(str).to_dict()
        
        # Count columns by data type using value_counts
        dtype_counts = df.dtypes.value_counts()
        profile['dtype_distribution'] = dtype_counts.to_dict()
        
        # ============================================================
        # MISSING VALUE ANALYSIS - Vectorized with NumPy
        # ============================================================
        # Use Pandas isnull() which is vectorized over entire DataFrame
        missing_matrix = df.isnull()
        missing_counts = missing_matrix.sum()  # Vectorized column-wise sum
        missing_pct = (missing_counts / len(df) * 100).round(2)
        
        profile['missing_values'] = missing_counts.to_dict()
        profile['missing_percentages'] = missing_pct.to_dict()
        
        # Use boolean masking to filter columns with missing values
        columns_with_missing = missing_counts[missing_counts > 0]
        
        if not columns_with_missing.empty:
            print(f"\n[WARNING] Missing Values Detected:")
            # Use Pandas iteritems() for efficient iteration over Series
            for col, count in columns_with_missing.items():
                pct = missing_pct[col]
                print(f"   {col}: {count:,} ({pct}%)")
        else:
            print("[SUCCESS] No missing values")
        
        # ============================================================
        # DUPLICATE ROW DETECTION - Vectorized
        # ============================================================
        # duplicated() returns boolean Series - vectorized operation
        duplicate_mask = df.duplicated()
        duplicate_count = duplicate_mask.sum()  # NumPy sum over boolean array
        
        profile['duplicate_rows'] = int(duplicate_count)
        profile['duplicate_row_percentage'] = round(duplicate_count / len(df) * 100, 2)
        
        if duplicate_count > 0:
            print(f"\n[WARNING] Duplicate Rows: {duplicate_count:,} ({profile['duplicate_row_percentage']}%)")
        else:
            print("[SUCCESS] No duplicate rows")
        
        # ============================================================
        # ID COLUMN ANALYSIS - Using Pandas string methods and nunique()
        # ============================================================
        # Use vectorized string operation to find ID columns
        id_columns = df.columns[df.columns.str.contains('id', case=False, na=False)]
        
        if len(id_columns) > 0:
            print(f"\n[ANALYSIS] ID Column Analysis:")
            
            # Vectorized nunique() for all ID columns at once
            unique_counts = df[id_columns].nunique()
            null_counts = df[id_columns].isnull().sum()
            
            profile['id_column_analysis'] = {}
            
            for col in id_columns:
                unique_count = unique_counts[col]
                null_count = null_counts[col]
                duplicate_ids = len(df) - unique_count
                is_unique = (duplicate_ids == 0) and (null_count == 0)
                
                profile['id_column_analysis'][col] = {
                    'unique_values': int(unique_count),
                    'duplicate_count': int(duplicate_ids),
                    'null_count': int(null_count),
                    'cardinality_ratio': round(unique_count / len(df), 4),
                    'is_potential_primary_key': is_unique
                }
                
                status = "[PK] Unique (Potential Primary Key)" if is_unique else f"[WARNING] {duplicate_ids:,} duplicates"
                print(f"   {col}: {unique_count:,} unique values - {status}")
        
        # ============================================================
        # NUMERIC COLUMN STATISTICS - Using Pandas describe()
        # ============================================================
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            # describe() generates all statistics in one vectorized operation
            numeric_stats = df[numeric_cols].describe()
            profile['numeric_statistics'] = numeric_stats.to_dict()
            
            # Additional statistics using vectorized operations
            numeric_stats_extended = pd.DataFrame({
                'min': df[numeric_cols].min(),
                'max': df[numeric_cols].max(),
                'mean': df[numeric_cols].mean(),
                'median': df[numeric_cols].median(),
                'std': df[numeric_cols].std(),
                'skewness': df[numeric_cols].skew(),  # Vectorized skewness
                'kurtosis': df[numeric_cols].kurtosis(),  # Vectorized kurtosis
                'zeros': (df[numeric_cols] == 0).sum(),  # Count zeros using boolean mask
                'negatives': (df[numeric_cols] < 0).sum()  # Count negatives
            })
            
            profile['numeric_extended_stats'] = numeric_stats_extended.to_dict()
            
            print(f"\n[ANALYSIS] Numeric Columns: {len(numeric_cols)}")
            
            # Use boolean masking to find price/value columns
            price_cols = numeric_cols[numeric_cols.str.contains('price|value|freight', case=False, na=False)]
            
            for col in price_cols:
                stats = numeric_stats_extended.loc[col]
                print(f"   {col}: min={stats['min']:.2f}, max={stats['max']:.2f}, " 
                      f"mean={stats['mean']:.2f}, median={stats['median']:.2f}")
                
                # Flag suspicious values
                if stats['negatives'] > 0:
                    print(f"      [WARNING] {int(stats['negatives'])} negative values detected!")
                if stats['zeros'] > 0:
                    pct_zeros = stats['zeros'] / len(df) * 100
                    print(f"      [INFO] {int(stats['zeros'])} zero values ({pct_zeros:.1f}%)")
        
        # ============================================================
        # CATEGORICAL COLUMN ANALYSIS - Using value_counts()
        # ============================================================
        categorical_cols = df.select_dtypes(include=['object']).columns
        # Exclude ID columns from categorical analysis
        categorical_cols = categorical_cols[~categorical_cols.str.contains('id', case=False, na=False)]
        
        if len(categorical_cols) > 0:
            print(f"\n[ANALYSIS] Categorical Columns: {len(categorical_cols)}")
            profile['categorical_analysis'] = {}
            
            for col in categorical_cols:
                unique_count = df[col].nunique()
                
                # Only show details for low-cardinality categoricals
                if unique_count <= 50:
                    # value_counts() is vectorized
                    value_counts = df[col].value_counts()
                    
                    profile['categorical_analysis'][col] = {
                        'unique_values': int(unique_count),
                        'mode': value_counts.index[0] if len(value_counts) > 0 else None,
                        'mode_frequency': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                        'top_5_values': value_counts.head(5).to_dict()
                    }
                    
                    print(f"   {col}: {unique_count} unique values, mode='{value_counts.index[0]}'")
        
        # ============================================================
        # DATE COLUMN ANALYSIS - Using pd.to_datetime() vectorized
        # ============================================================
        date_columns = df.columns[df.columns.str.contains('date|timestamp', case=False, na=False)]
        
        if len(date_columns) > 0:
            print(f"\n[ANALYSIS] Date Columns: {len(date_columns)}")
            profile['date_column_analysis'] = {}
            
            for col in date_columns:
                try:
                    # Vectorized date parsing
                    date_series = pd.to_datetime(df[col], errors='coerce')
                    
                    # Vectorized null checking
                    valid_mask = date_series.notna()
                    valid_dates = valid_mask.sum()
                    invalid_dates = (~valid_mask).sum()
                    
                    if valid_dates > 0:
                        # Vectorized min/max operations
                        min_date = date_series.min()
                        max_date = date_series.max()
                        date_range_days = (max_date - min_date).days
                        
                        profile['date_column_analysis'][col] = {
                            'valid_dates': int(valid_dates),
                            'invalid_dates': int(invalid_dates),
                            'min_date': str(min_date),
                            'max_date': str(max_date),
                            'date_range_days': int(date_range_days)
                        }
                        
                        print(f"   {col}: {min_date.date()} to {max_date.date()} ({date_range_days} days)")
                        if invalid_dates > 0:
                            print(f"      [WARNING] {invalid_dates} invalid dates ({invalid_dates/len(df)*100:.1f}%)")
                except Exception as e:
                    profile['date_column_analysis'][col] = {'error': str(e)}
                    print(f"   {col}: [ERROR] Failed to parse dates - {str(e)}")
        
        # ============================================================
        # CARDINALITY ANALYSIS - Using nunique() vectorized
        # ============================================================
        # Calculate cardinality for all columns at once
        cardinality = df.nunique()
        cardinality_ratio = (cardinality / len(df) * 100).round(2)
        
        profile['cardinality'] = cardinality.to_dict()
        profile['cardinality_ratio_pct'] = cardinality_ratio.to_dict()
        
        # Identify high-cardinality non-ID columns (potential data quality issues)
        high_cardinality = cardinality_ratio[(cardinality_ratio > 95) & 
                                             (~cardinality.index.str.contains('id', case=False, na=False))]
        
        if not high_cardinality.empty:
            print(f"\n[ANALYSIS] High Cardinality Non-ID Columns (>95% unique):")
            for col, ratio in high_cardinality.items():
                print(f"   {col}: {ratio}% unique values")
        
        # ============================================================
        # SAMPLE DATA - Using head()
        # ============================================================
        profile['sample_data'] = df.head(3).to_dict()
        
        return profile
    
    def profile_all_files(self, chunk_size: int = 100000):
        """
        Profile all discovered Olist CSV files.
        
        Args:
            chunk_size: Chunk size for large files
        """
        files = self.discover_olist_files()
        
        if not files:
            print("[ERROR] No Olist CSV files found!")
            return
        
        print(f"\n[INFO] Discovered {len(files)} Olist data files:")
        for f in files:
            print(f"   • {f.name}")
        
        # Profile each file
        for file_path in files:
            # Use chunking for geolocation (known to be large)
            chunk = chunk_size if 'geolocation' in file_path.name.lower() else None
            profile = self.profile_file(file_path, chunk)
            self.profile_results[file_path.name] = profile
    
    def analyze_relationships(self, file1_name: str, file2_name: str, key_column: str):
        """
        Analyze relationship between two files using Pandas merge operations.
        
        This demonstrates:
        - Pandas merge for relationship validation
        - Vectorized set operations
        - Referential integrity checking
        
        Args:
            file1_name: First file name
            file2_name: Second file name
            key_column: Column to join on
        """
        print(f"\n{'='*80}")
        print(f"RELATIONSHIP ANALYSIS: {file1_name} ↔ {file2_name}")
        print(f"{'='*80}")
        
        try:
            # Load both files
            df1 = pd.read_csv(self.data_dir / file1_name)
            df2 = pd.read_csv(self.data_dir / file2_name)
            
            # Get unique keys using vectorized operations
            keys1 = df1[key_column].dropna().unique()
            keys2 = df2[key_column].dropna().unique()
            
            # Use NumPy set operations (highly optimized)
            common_keys = np.intersect1d(keys1, keys2)
            only_in_file1 = np.setdiff1d(keys1, keys2)
            only_in_file2 = np.setdiff1d(keys2, keys1)
            
            print(f"\n[KEY] Column: {key_column}")
            print(f"   {file1_name}: {len(keys1):,} unique keys")
            print(f"   {file2_name}: {len(keys2):,} unique keys")
            print(f"   Common keys: {len(common_keys):,}")
            
            if len(only_in_file1) > 0:
                print(f"   [WARNING] Keys only in {file1_name}: {len(only_in_file1):,}")
            
            if len(only_in_file2) > 0:
                print(f"   [WARNING] Keys only in {file2_name}: {len(only_in_file2):,}")
            
            # Calculate referential integrity percentage
            ref_integrity_pct = len(common_keys) / len(keys1) * 100 if len(keys1) > 0 else 0
            print(f"   Referential Integrity: {ref_integrity_pct:.2f}%")
            
        except Exception as e:
            print(f"[ERROR] {e}")
    
    def generate_reports(self):
        """
        Generate comprehensive text and CSV reports from profiling results.
        """
        if not self.profile_results:
            print("[ERROR] No profiling results to report!")
            return
        
        # Generate text report
        report_path = self.output_dir / 'data_profile_report.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("OLIST ANALYTICS PRO - DATA PROFILING REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Files Profiled: {len(self.profile_results)}\n")
            f.write("="*80 + "\n\n")
            
            for filename, profile in self.profile_results.items():
                f.write(f"\n{'='*80}\n")
                f.write(f"FILE: {filename}\n")
                f.write(f"{'='*80}\n")
                
                if 'error' in profile:
                    f.write(f"[ERROR]: {profile['error']}\n")
                    continue
                
                f.write(f"File Size: {profile.get('file_size_mb', 0):.2f} MB\n")
                f.write(f"Rows: {profile.get('row_count', 0):,}\n")
                f.write(f"Columns: {profile.get('column_count', 0)}\n")
                f.write(f"Duplicate Rows: {profile.get('duplicate_rows', 0):,} ({profile.get('duplicate_row_percentage', 0)}%)\n\n")
                
                f.write("COLUMNS:\n")
                for col in profile.get('columns', []):
                    dtype = profile.get('data_types', {}).get(col, 'unknown')
                    missing = profile.get('missing_values', {}).get(col, 0)
                    missing_pct = profile.get('missing_percentages', {}).get(col, 0)
                    f.write(f"  • {col:40s} {dtype:15s} Missing: {missing:,} ({missing_pct}%)\n")
                
                # ID columns
                if profile.get('id_column_analysis'):
                    f.write("\nID COLUMN ANALYSIS:\n")
                    for col, stats in profile['id_column_analysis'].items():
                        f.write(f"  • {col}:\n")
                        f.write(f"      Unique values: {stats['unique_values']:,}\n")
                        f.write(f"      Duplicates: {stats['duplicate_count']:,}\n")
                        f.write(f"      Potential PK: {stats['is_potential_primary_key']}\n")
                
                # Date columns
                if profile.get('date_column_analysis'):
                    f.write("\nDATE COLUMN ANALYSIS:\n")
                    for col, stats in profile['date_column_analysis'].items():
                        if 'error' not in stats:
                            f.write(f"  • {col}: {stats['min_date']} to {stats['max_date']}\n")
                
                f.write("\n")
        
        print(f"\n[SUCCESS] Text report saved: {report_path}")
        
        # Generate summary CSV
        summary_data = []
        for filename, profile in self.profile_results.items():
            if 'error' not in profile:
                summary_data.append({
                    'filename': filename,
                    'file_size_mb': round(profile.get('file_size_mb', 0), 2),
                    'row_count': profile.get('row_count', 0),
                    'column_count': profile.get('column_count', 0),
                    'duplicate_rows': profile.get('duplicate_rows', 0),
                    'duplicate_row_pct': profile.get('duplicate_row_percentage', 0),
                    'columns_with_missing': len([v for v in profile.get('missing_values', {}).values() if v > 0])
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_path = self.output_dir / 'data_profile_summary.csv'
        summary_df.to_csv(summary_path, index=False)
        print(f"[SUCCESS] Summary CSV saved: {summary_path}")
        
        # Generate data quality summary
        quality_issues = []
        for filename, profile in self.profile_results.items():
            if 'error' in profile:
                continue
                
            # Missing values
            for col, count in profile.get('missing_values', {}).items():
                if count > 0:
                    quality_issues.append({
                        'filename': filename,
                        'issue_type': 'Missing Values',
                        'column': col,
                        'count': count,
                        'percentage': profile.get('missing_percentages', {}).get(col, 0)
                    })
            
            # Duplicate IDs
            for col, stats in profile.get('id_column_analysis', {}).items():
                if stats['duplicate_count'] > 0:
                    quality_issues.append({
                        'filename': filename,
                        'issue_type': 'Duplicate IDs',
                        'column': col,
                        'count': stats['duplicate_count'],
                        'percentage': round(stats['duplicate_count'] / profile['row_count'] * 100, 2)
                    })
        
        if quality_issues:
            quality_df = pd.DataFrame(quality_issues)
            quality_path = self.output_dir / 'data_quality_issues.csv'
            quality_df.to_csv(quality_path, index=False)
            print(f"[SUCCESS] Quality issues saved: {quality_path}")
        else:
            print("[SUCCESS] No major data quality issues detected!")


def main():
    """
    Main execution function for data profiling.
    """
    print("\n" + "="*80)
    print("OLIST ANALYTICS PRO - DATA PROFILING")
    print("="*80)
    
    # Setup paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'dataset'
    output_dir = project_root / 'reports'
    
    # Create profiler and run
    profiler = DataProfiler(data_dir, output_dir)
    profiler.profile_all_files(chunk_size=100000)
    profiler.generate_reports()
    
    print("\n" + "="*80)
    print("[SUCCESS] DATA PROFILING COMPLETE!")
    print("="*80)
    print(f"\nReports saved to: {output_dir}")
    print("\nNext Steps:")
    print("  1. Review the data_profile_report.txt")
    print("  2. Investigate data quality issues")
    print("  3. Plan data cleaning strategies")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
