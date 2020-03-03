# extracts the hours of wait from tweet to numeric for Edmonds and Kingston
# ferry terminals.

# import necessary packages
import pandas as pd
import glob
import re


def load_data(path):
    """Loads the data from the regex path with standardized column names."""
    # load data
    all_files = glob.glob(path)
    df_from_each_file = (pd.read_csv(f) for f in all_files)
    df = pd.concat(df_from_each_file, ignore_index=True)

    # reformat column names
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # return the dataframe with columns tweet_text and time
    return df[['tweet_text', 'time']]


def get_num(text):
    """Returns the number contained in the text (assumes only one number 
    between 1 and 3, text or numeric). Returns 0 if text includes no, 
    extenced, and wait."""
    if bool(re.search('1|one|60 minute', text)): return 1
    elif bool(re.search('2|two', text)): return 2
    elif bool(re.search('3|three', text)): return 3
    elif bool(re.search('4|four', text)): return 4
    elif bool(re.search('90 min', text)): return 1.5
    elif bool(re.search('no.*wait', text)): return 0
    else: return None


def get_hour(text, locName, otherLocName, altNames):
    """Returns the hour of wait described in the text for the location name
    
    Args:
      text: a string describing the wait
      locName: the name of the location to extract the time for
      otherLocName: the name of the location NOT getting times extracted
      altNames: a dictionary of the short names for locations 
                (eg. {'Edmonds': ['edm', 'edms', 'ed'],
                      'Kingston': [kgstn', 'king']})
      
    Returns: and int - the number of hours wait for the locName
    """
    # initialize hour and backup hour
    hour = None
    backup_hour = None
    
    # check for locName
    if locName not in text:
        return hour
    
    # check for otherLocName (ie. a dual-location message), and get the number for solo messages
    if otherLocName not in text:
        hour = get_num(text)
        
    # otherwise it's a dual-location message
    else:
        # split the message on - and ,
        split_texts = re.split('-|,', text)
        for split_text in split_texts:
            # initialize flag of this section containing the location of interest
            loc_in_text = False
            
            # check for full name and alternate/abreviated names
            if locName in split_text:
                loc_in_text = True
            for name in altNames[locName]:
                if name in split_text:
                    loc_in_text = True
            
            # if the location is in the split, get the hour
            if loc_in_text:
                hour = get_num(split_text)
            
            # if the location isn't in the split, get the hour as a backup
            else:
                backup_hour = get_num(split_text)
                
        # if none of the sections have the name and hour together, use the backup_hour
        if hour == None:
            hour = backup_hour
    return hour



def get_hours(texts, locName, otherLocName, altNames):
    """Returns the hours of wait described in the texts for the location name
    
    Args:
      texts: a panadas series of text describing the waits
      locName: the name of the location to extract the time for
      otherLocName: the name of the location NOT getting times extracted
      altNames: a dictionary of the short names for locations 
                (eg. {'edmonds': ['edm', 'edms', 'ed'],
                        'kingston': ['kgstn', 'king']})
      
    Returns: list of ints representing the wait hours in each record of text 
            for the specified location
    """
    return [get_hour(text, locName, otherLocName, altNames) for text in texts]


def clip_tweets(df, copy=True):
    """Clips the tweets in column 'tweet_text' by removing the url, route 
    indicator, and wsp boarding pass indicator.

    Args:
        df: Pandas dataframe with column 'tweet_text'
        copy: Bool - transform a copy of the dataframe

    Returns: a dataframe with column 'tweet_text' transformed
    """
    # copy the dataframe (or not)
    if copy == True:
        df = df.copy()
    
    # removing the url, 
    df['tweet_text'] = df['tweet_text'].str.replace('https:.*', '')

    # remove route indicator ('edm/king -'), extra whitespace
    df['tweet_text'] = df['tweet_text'].str.replace('edm/king -', '')
    df['tweet_text'] = df['tweet_text'].str.strip()

    # remove boarding pass indicator
    wsp_txt = ', no wsp boarding pass required|, wsp boarding pass required'
    df['tweet_text'] = df['tweet_text'].str.replace(wsp_txt, '')

    # return the dataframe
    return df


def filter_tweets(df, locName):
    """filters the tweets for those regarding waits at the location.

    Args:
        df: a dataframe with column 'tweet_text'
        locName: the name of the location of interest
    """
    df_wait = df[df['tweet_text'].str.contains('wait')]
    df_filtered = df_wait[df_wait['tweet_text'].str.contains(locName)].copy()
    return df_filtered


def main():
    """extracts the hours of wait from tweet to numeric for Edmonds and 
    Kingston ferry terminals.
    """
    # load data from csv
    df = load_data("../data/raw/*.csv")

    # convert to lowercase
    df_lower = df.copy()
    df_lower['tweet_text'] = df_lower['tweet_text'].str.lower()

    # clip url, route, boarding pass notices
    df_clipped = clip_tweets(df_lower)

    # set alternate names for routes
    altNames = {'edmonds': ['edm', 'edms', ' ed'], 
                'kingston': ['kgstn', 'king']}

    # get the edmonds wait times
    ed_df = filter_tweets(df_clipped, 'edmonds')
    ed_df['wait_time']  = get_hours(ed_df['tweet_text'],
                                    'edmonds',
                                    'kingston',
                                    altNames)

    # get the kingston wait times
    ki_df = filter_tweets(df_clipped, 'kingston')
    ki_df['wait_time']  = get_hours(texts=ki_df['tweet_text'],
                                    locName='kingston',
                                    otherLocName='edmonds',
                                    altNames=altNames)

    # save dataframes as csv
    ed_df.to_csv('../data/hour_extracted/edmonds.csv', index=False)
    ki_df.to_csv('../data/hour_extracted/kingston.csv', index=False)


if __name__ == "__main__":
    main()