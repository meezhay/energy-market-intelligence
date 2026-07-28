# all cleaning and preparing data functions will be in this file

def merge_metadata(df, metadata):
    return df.merge(
        metadata,
        on="Country Code",
        how="left"
    )


def filter_ssa(df):
    return df[df["Region"] == "Sub-Saharan Africa"]


def select_years(start=2014, end=2023):
    return [str(year) for year in range(start, end + 1)]