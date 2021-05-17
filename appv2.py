"""
## App: URL AB Beta Testing App with Streamlit
Author: 
Source: 
Description:
This is a prototype built with the Streamlit Framework and Google News RSS.
Purpose:
Allow users to paste a URL address to find title, media source, and publishing date for any news publication. 
"""
# Core Pkgs
import streamlit as st 
import pandas as pd

import feedparser
import urllib
import json
import csv
from datetime import datetime

import base64
import yaml
import os

import errors

from PIL import Image

####################################################################
### Download URL Function ### 
####################################################################

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.
    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.
    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')
    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

@errors.exception_handler
def main():
    """ URL Parse API APP with Streamlit """

    # Title
    st.title("Article Clipper Helper")
    
    # display image
    image = Image.open("ab_ws_logo.png")
    st.image(image, use_column_width=True)
    
    st.subheader("Paste URL(s) Here:")

    ####################################################################
    ### User Input Fields ###
    ####################################################################

    # User input -- User pastes all links here 
    user_url = st.text_input("Paste Link(s) Here:","")

    # Convert user input urls to str type
    urls = str(user_url)

    ####################################################################
    ### Extract URL Article Info ### 
    ####################################################################

    # Create a submission button to parse URL information 
    if st.button("Get URL Info"):
        # transform user urls to a list 
        #urls = str(user_url)
 
        new_urls = []

        # Separate user input URLs 
        splited = urls.split("http")
        for each in splited:
            if "://" in each:
                new_urls.append("http" + each.strip())

        data = []
        # Output column names 
        columns = ['Article Title','Date', 'Outlet Name', 'Links']
        for s in new_urls:
            # Insert urls into google news url & query RSS feed
            url = "https://news.google.com/rss/search?q=" + s  

            d = feedparser.parse(url)
            if len(d['entries']) == 0:
                data.append(['NaN', 'NaN', 'NaN', s])
            try:
                for i, entry in enumerate(d.entries, 1):
                    p = entry.published_parsed
                    sortkey = "%04d%02d%02d%02d%02d%02d" % (p.tm_year, p.tm_mon, p.tm_mday, p.tm_hour, p.tm_min, p.tm_sec)
                    datetime_obj = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
                    tmp = {
                        "no" : i,
                        "title" : entry.title,
                        "summery" : entry.summary,
                        "link" : entry.link,
                        "published" : entry.published,
                        "sortkey" : sortkey,
                        "source": entry.source
                    }
                    if tmp['link'] == s:
                        src_ttl = tmp['source']['title'].split(".")[0].strip()
                        data.append([tmp['title'],datetime_obj.strftime("%m/%d/%y"),src_ttl, tmp['link']])
            except:
                print(f"No data returned for {s}")


        df = pd.DataFrame(data=data, columns=columns)
        
        ###################### New Edits ##############
        # config path
        cfg_path = "config/config.yaml"
        cfg = yaml.safe_load(open(cfg_path))

        outlet_df = pd.read_csv('outlet_reference.csv')

        # create temp df
        tmp_df = pd.DataFrame(columns=[*range(42)])
        tmp_df = tmp_df.rename(columns=cfg["tracker_cols"])

        new_df = tmp_df.append(df)
        new_df[['Outlet Reach (Weekly)','Outlet Reach (Monthly)']] = new_df[['Outlet Reach (Weekly)','Outlet Reach (Monthly)']].apply(pd.to_numeric)

        output_df = pd.merge(df, outlet_df, on="Outlet Name", how="left")
        output_df = pd.concat([tmp_df, output_df])

        st.dataframe(output_df)

        # write to file for download
        tmp_download_link = download_link(
            output_df,
            "output.csv",
            "Click here to download!",
        )
        st.markdown(tmp_download_link, unsafe_allow_html=True)

if __name__ == '__main__':
	main()