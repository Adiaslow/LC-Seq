# lcseq/scripts/subset_peptides.py
"""This script subsets a peptide library CSV file based on building block composition.

Example Usage:
    # Find all peptides with Leu in position 1 and Phe in position 2
    python scripts/subset_peptides.py  \
        tests/data/raw_data.csv \
        tests/data/raw_data_subset.csv \
        tests/data/raw_data_column_mapping.yaml \
        --bb1 "Leu,βHomoleu,Leu-LeuMe-Pro" \
        --bb2 "Phe,Nvl,Leu-LA03-Pro" \
        --bb3 "Val,LA03,LeuMe-DLeuMe-Pro" \
        --include-truncations \
        --null-identifier "AgxNull"
"""
from pathlib import Path
import click
import pandas as pd
from typing import List, Dict, Optional
import yaml
from itertools import combinations

def load_column_mapping(config_path: Path) -> Dict[str, List[str]]:
    """Load building block column mapping from config file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['building_block_columns']['name']

def create_filter_conditions(
    df: pd.DataFrame,
    bb_columns: List[str],
    bb_filters: List[List[str]]
) -> pd.Series:
    """Create filter conditions for each position."""
    conditions = pd.Series(True, index=df.index)

    for col, allowed_bbs in zip(bb_columns, bb_filters):
        if allowed_bbs:  # Only apply filter if building blocks specified
            conditions &= df[col].isin(allowed_bbs)

    return conditions

def find_truncations(
    row: pd.Series,
    bb_columns: List[str],
    bb_filters: List[List[str]],
    null_identifier: str = "AgxNull"
) -> List[pd.Series]:
    """Generate all possible truncations of a peptide."""
    truncations = []
    n = len(bb_columns)

    def make_sequence(mask):
        """Create sequence based on binary mask."""
        trunc_row = row.copy()
        for i, keep in enumerate(mask):
            if not keep:
                trunc_row[bb_columns[i]] = null_identifier
        return trunc_row

    # For each number of nulls (0 to n)
    for num_nulls in range(n + 1):
        # Get all combinations of positions that will be null
        for null_positions in combinations(range(n), num_nulls):
            # Check if the non-null positions have valid building blocks
            valid = True
            for i in range(n):
                if i not in null_positions:  # If this position keeps its building block
                    if bb_filters[i] and row[bb_columns[i]] not in bb_filters[i]:
                        valid = False
                        break

            if valid:
                # Create pattern - start with all 1s (keep)
                pattern = [1] * n
                # Set null positions to 0
                for pos in null_positions:
                    pattern[pos] = 0
                truncations.append(make_sequence(pattern))

    return truncations

def parse_bb_list(ctx, param, value) -> List[str]:
    """Parse building block list, handling special characters and spaces."""
    if not value:
        return []
    return [bb.strip() for bb in value.split(',')]

@click.command()
@click.argument('input_csv', type=click.Path(exists=True, path_type=Path))
@click.argument('output_csv', type=click.Path(path_type=Path))
@click.argument('config_path', type=click.Path(exists=True, path_type=Path))
@click.option('--bb1', callback=parse_bb_list, help='Building blocks for position 1')
@click.option('--bb2', callback=parse_bb_list, help='Building blocks for position 2')
@click.option('--bb3', callback=parse_bb_list, help='Building blocks for position 3')
@click.option('--bb4', callback=parse_bb_list, help='Building blocks for position 4')
@click.option('--bb5', callback=parse_bb_list, help='Building blocks for position 5')
@click.option('--bb6', callback=parse_bb_list, help='Building blocks for position 6')
@click.option('--include-truncations/--no-truncations', default=False,
              help='Include truncated versions of matched peptides')
@click.option('--null-identifier', default='AgxNull',
              help='Identifier used for null/truncated positions')
def main(
    input_csv: Path,
    output_csv: Path,
    config_path: Path,
    bb1: List[str],
    bb2: List[str],
    bb3: List[str],
    bb4: List[str],
    bb5: List[str],
    bb6: List[str],
    include_truncations: bool,
    null_identifier: str,
):
    """Subset a peptide library CSV file based on building block composition."""
    # Load column mapping
    bb_column_mapping = load_column_mapping(config_path)
    bb_columns = list(bb_column_mapping)  # Convert mapping keys to list

    # Create bb_filters list from provided options
    all_bbs = [bb1, bb2, bb3, bb4, bb5, bb6]
    bb_filters = all_bbs[:len(bb_columns)]  # Only take as many as we have columns

    # Read input CSV
    click.echo(f"Reading input file: {input_csv}")
    df = pd.read_csv(input_csv, low_memory=False)
    total_peptides = len(df)
    click.echo(f"Found {total_peptides} total peptides in input file")

    # Display filter criteria
    for pos, (col, bbs) in enumerate(zip(bb_columns, bb_filters), 1):
        if bbs:
            click.echo(f"Position {pos} filter: {', '.join(bbs)}")
        else:
            click.echo(f"Position {pos}: No filter applied")

    # Apply building block filters
    mask = create_filter_conditions(df, bb_columns, bb_filters)
    filtered_df = df[mask].copy()

    initial_matches = len(filtered_df)
    click.echo(f"\nFound {initial_matches} peptides matching the specified criteria")

    if include_truncations and not filtered_df.empty:
        # Generate truncations for each matched peptide
        all_rows = []
        for _, row in filtered_df.iterrows():
            all_rows.append(row)  # Include the original row
            truncations = find_truncations(row, bb_columns, bb_filters, null_identifier)
            all_rows.extend(truncations)

        # Create new DataFrame with original matches and truncations
        filtered_df = pd.DataFrame(all_rows)

        # Remove duplicates
        filtered_df = filtered_df.drop_duplicates()

        truncation_count = len(filtered_df) - initial_matches
        click.echo(f"Generated {truncation_count} truncation variants")

    click.echo(f"\nTotal peptides in output: {len(filtered_df)}")
    click.echo(f"Writing output to: {output_csv}")
    filtered_df.to_csv(output_csv, index=False)

if __name__ == '__main__':
    main()
