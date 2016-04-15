#!/usr/bin/env python3

from ouroboros import ouroboros

import pandas as pd
import numpy as np

import jellyfish
import bitarray

from multiprocessing import Pool
import itertools
import argparse
import logging
import sys
import os


def cols_stats(df):
    """Return stats for each column"""
    stats = pd.DataFrame(index=df.columns)
    
    stats['positives'] = df.count()
    stats['alones'] = df[df.count(axis=1) == 1].count()
    stats['distincts'] = df.apply(lambda col: col.dropna().unique().size)
    
    bitarrays = {av: bitarray.bitarray(~col.isnull())
                 for av, col in df.iteritems()}
    
    for av1 in df.columns:
        overlaps = list()
        vec1 = bitarrays[av1]
        
        for av2 in df.columns:
            if av1 == av2:
                continue
                
            vec2 = bitarrays[av2]

            r_xor = vec1 ^ vec2
            r_11 = sum(vec1 & vec2)
            r_10 = sum(r_xor & vec1)
            r_01 = sum(r_xor & vec2)
            r_00 = sum(~(vec1 | vec2))
            
            assert (r_11 + r_10 + r_01 + r_00) == len(vec2) == len(vec1)
            
            d = 0
            dividend = r_11
            divisor = r_11 + min(r_10, r_01)
        
            if dividend and divisor: # handle division error
                d = dividend / divisor
            
            overlaps.append(d)
            
        stats.ix[av1, 'overlap'] = np.mean(overlaps)
        stats.ix[av1, 'overlap_min'] = np.min(overlaps)
        stats.ix[av1, 'overlap_max'] = np.max(overlaps)
        
    return stats


def row_stats(in_row):
    """Compute additional stats for each row"""
    out_row = {}
    index, row = in_row

    out_row['index'] = index
    out_row['positives'] = row.count()
    out_row['distincts'] = row.dropna().unique().size
    out_row['max'] = row.value_counts().max()

    labels = row.dropna()

    if labels.size < 2:
        out_row['similarity'] = np.nan
    else:
        similarities = []

        for l1, l2 in itertools.combinations(labels, 2):
            s = jellyfish.jaro_winkler(l1, l2)
            similarities.append(s)

        out_row['resemblance'] = np.mean(similarities)
        out_row['resemblance_min'] = np.min(similarities)
        out_row['resemblance_max'] = np.max(similarities)

    return out_row


def rows_stats(df):
    """Return stats for each column"""
    pool = Pool()
    out_rows = pool.map(row_stats, df.iterrows())
    pool.close()
    pool.join()
    
    return pd.DataFrame.from_records(out_rows, index='index')


def stase_metrics(df):
    """Compute STASE metrics for a given dataset"""
    M, N = df.shape
    logging.info("FILES: {0}, ANTIVIRUS: {1}".format(M, N))

    clusters = df.stack().value_counts()
    logging.info("clustering DONE")
    
    O = clusters.size
    logging.info("LABELS: {0}".format(O))
    
    apps = rows_stats(df)
    logging.info("rowstats computation DONE")

    avs = cols_stats(df)
    logging.info("colstats computation DONE")

    m = pd.Series()
    m['equiponderance'], m['equiponderance_idx'] = ouroboros(avs['positives'], True)
    m['exclusivity'] = avs['alones'].sum() / M
    m['recognition'] = apps['positives'].mean() / N
    m['synchronicity'] = np.mean(avs['overlap'])
    m['genericity'] = 1 - (O-1) / (avs['positives'].sum()-1)
    m['uniformity'], m['uniformity_idx'] = ouroboros(clusters, True)
    m['divergence'] = (apps['distincts'].sum() - M) / (apps['positives'].sum() - M)
    m['consensuality'] = (apps['max'].sum() - M) / (apps['positives'].sum() - M)
    m['resemblance'] = np.mean(apps['resemblance'].dropna())
    m['avs'] = N
    m['apps'] = M
    m['labels'] = O

    logging.info("metrics computation DONE")
    
    return m, apps, avs, clusters


def stase_metrics_from_csv(csvpath):
    """Compute stase metrics for a CSV file"""
    df = pd.read_csv(csvpath, index_col=0, dtype=str)

    return stase_metrics(df)


def parse(arguments):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('infile', help="Input file in CSV format")
    parser.add_argument('outfile', help="Output file in JSON format")
    
    return parser.parse_args(arguments)


if __name__ == '__main__':
    logging.basicConfig(format="[%(levelname)s] %(asctime)s: %(message)s", level=logging.INFO)
    args = parse(sys.argv[1:])

    cwd = os.getcwd()
    infile = os.path.join(cwd, args.infile)
    outfile = os.path.join(cwd, args.outfile)

    logging.info("Using as input file: {0}".format(infile))
    metrics, apps, avs, clusters = stase_metrics_from_csv(infile)

    logging.info("Using as output file: {0}".format(outfile))
    metrics.to_json(outfile)

    print(metrics)

    logging.info('Done.')
