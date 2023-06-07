import pandas as pd
import argparse

def read_dataset(dataset_file_path):
    df = pd.read_csv(dataset_file_path, encoding='utf-8', keep_default_na=False)
    return df

def trim_dataset(df):
    df = df[df['label'] != 'X']
    df = df[['sentence', 'label']]
    return df

def write_dataset(df, dataset_file_path):
    df.to_csv(dataset_file_path, encoding='utf-8', index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', '-d', type=str, help='Path to the dataset file')
    args = parser.parse_args()

    dataset_df = read_dataset(args.dataset)
    trimmed_dataset_df = trim_dataset(dataset_df)
    write_dataset(trimmed_dataset_df, './output/trimmed_dataset.tsv')