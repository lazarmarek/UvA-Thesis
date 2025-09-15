import feedparser
import requests
import time
from pathlib import Path
import os
import pandas as pd
from dotenv import load_dotenv

class ArticleDownloader:
    """
    A class to download research articles currently supporting arXiv & Open Science Framework (OSF).

    """
    def arxiv_download(self, name, email, max_results=3, sleep_time=3.0, download_dir="./arxiv_downloads"):
        """
        Search arXiv and download the first `max_results` articles.

        Args:
            name (str): Name of the user for the User-Agent header.
            email (str): Email of the user for the User-Agent header.
            max_results (int): Number of results to download.
            sleep_time (float): Sleep time between downloads.
            download_dir (str): Directory to save PDFs.
        """
        # Ensure the download directory exists
        Path(download_dir).mkdir(parents=True, exist_ok=True)

        # Build the query URL
        base_url = "http://export.arxiv.org/api/query?"
        header = {"User-Agent": f"{name} <{email}>"}
        query = f"search_query=all&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        feed = feedparser.parse(base_url + query)

        for i, entry in enumerate(feed.entries):
            try:
                pdf_url = entry.id.replace('abs', 'pdf') + ".pdf"
                arxiv_id = entry.id.split('/')[-1]
                filename = Path(download_dir) / f"{arxiv_id}.pdf"

                # Download the PDF
                print(f"Downloading {i+1}/{len(feed.entries)}: {arxiv_id}...")
                response = requests.get(pdf_url, headers=header)
                response.raise_for_status()  # Raise an error for bad responses

                # Save the PDF
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded & Saved: {filename}")
                
                # Sleep between downloads (except for the last one)
                if i < len(feed.entries) - 1:
                    time.sleep(sleep_time)

            except Exception as e:
                print(f"Error downloading {entry.id}: {e}")

        print("All downloads completed.")

    def osf_download(self, subjects, max_results, download_dir="./osf_downloads"):
        """
        Download preprints from the Open Science Framework (OSF) based on subjects.

        Args:
            subjects (list): List of subjects to filter preprints.
            download_dir (str): Directory to save downloaded articles.

        """
        # Defining helper functions
        ## Metadata fetcher
        def fetch_preprints_metadata(subject : str, limit : int=1, page_size : int=max_results):
            base_url = 'https://api.osf.io/v2/preprints'
            params = {
                'filter[subjects]': subject,
                'page[size]': page_size
            }

            preprints = []
            url = base_url
            iteration = 0
            while url and iteration < limit:
                iteration += 1
                if url == base_url:
                    response = requests.get(url, params=params, headers=HEADERS)
                else:
                    response = requests.get(url, headers=HEADERS)
                time.sleep(1)
                data = response.json()

                # Check if the preprint licenses are CC-BY 4.0
                for preprint in data['data']:

                    # Check if the 'relationships' key is in the 'preprints' dictionary,
                    # and then if the 'license' key is inside that dictionary
                    if not preprint.get('relationships', {}).get('license'):
                        continue
                    
                    if preprint['relationships']['license']['data']['id'] in ccby4_ids:
                        preprints.append(preprint)

                url = data['links'].get('next')
            return preprints
        ## Get Contributors
        def get_contributors(contributors_url):
            if contributors_url is None:
                return []
            response = requests.get(contributors_url, headers=HEADERS)
            data = response.json()
            contributors = []
            for contributor in data['data']:
                contributors.append(contributor['embeds']['users']['data']['attributes']['full_name'])
            return contributors
        ## Get PDF URL
        def get_pdf_url(files_url):
            if files_url is None:
                return None, None

            response = requests.get(files_url + '/versions/', headers=HEADERS)
            data = response.json()

            for file in data['data']:
                if file['links'].get('download'):
                    download_url = file['links']['download']
                    filename = file.get('attributes', {}).get('name', 'unknown')
                    return download_url, filename
            
            return None, None
        def process_preprints(preprints, subject):
            abbr_subj = subject.split(' ')[0].lower()
            articles_dir = Path(download_dir) / f"{abbr_subj}_articles"
            articles_dir.mkdir(parents=True, exist_ok=True)

            metadata_list = []
            
            for preprint in preprints:
                title = preprint.get('attributes', {}).get('title')
                date =  preprint.get('attributes', {}).get('date_published')
                doi = preprint.get('attributes', {}).get('doi')
                reviewed_doi = preprint.get('links', {}).get('preprint_doi')
                
                contributors_url = preprint.get('relationships', {}).get(
                    'contributors', {}).get('links', {}).get('related', {}).get('href')
                authors = get_contributors(contributors_url)

                pdf_url = preprint.get('relationships', {}).get('primary_file', {}).get(
                    'links', {}).get('related', {}).get('href')
                
                dl_url, filename = get_pdf_url(pdf_url)

                license = ccby4_ids[preprint['relationships']['license']['data']['id']]

                metadata = {
                    'title': title,
                    'date': date,
                    'doi': doi,
                    'peer_reviewed_doi': reviewed_doi,
                    'name': filename,
                    'authors': authors,
                    'pdf_url': pdf_url,
                    'dl_url': dl_url,
                    'license': license
                }
                metadata_list.append(metadata)

                # Don't download the PDF if no URL is available or the license isn't regular CC-BY 4.0
                if (metadata['dl_url'] is None or
                    metadata['license'] != 'CC-By Attribution 4.0 International'):
                    continue

                # Create filename path
                file_extension = filename.split('.')[-1] if filename and '.' in filename else 'pdf'
                base_name = title.replace('/', '_').replace('\\', '_').replace(':', '_').replace(' ', '_')
                base_name = base_name[:20]  # Limit the base name length to avoid file
                pdf_filename = articles_dir / f"{base_name}.{file_extension}"
                
                # Check if file already exists
                if pdf_filename.exists():
                    print(f"File already exists, skipping: {pdf_filename}")
                    continue

                # Download
                try:
                    print(f"Downloading: {base_name}.{file_extension}")
                    pdf_response = requests.get(metadata['dl_url'], headers=HEADERS)
                    pdf_response.raise_for_status()  # Raise an error for bad responses
                    
                    with open(pdf_filename, 'wb') as f:
                        f.write(pdf_response.content)
                    print(f"Successfully downloaded: {pdf_filename}")
                    
                except Exception as e:
                    print(f"Error downloading {title}: {e}")

            return metadata_list

        # Load API token from .env file
        load_dotenv()
        try:
            api_token = os.environ["OSF_API_TOKEN"]
        except KeyError:
            print("API key not found. Please set 'OSF_API_TOKEN' in your .env file.")

        # Set the headers for the request
        HEADERS = {'Authorization': f'Bearer {api_token}'}

        # Set a licenses variable to filter results
        ccby4_ids = {
            '563c1cf88c5e4a3877f9e96a': 'CC-By Attribution 4.0 International',
            '60bf983b58510b0009a5a9a4': 'CC-BY Attribution-No Derivatives 4.0 International',
            '60bf992258510b0009a5a9a6': 'CC-BY Attribution-NonCommercial 4.0 International',
            '60bf99e058510b0009a5a9a9': 'CC-BY Attribution-NonCommercial-ShareAlike 4.0 International'
        }

        # Batch process multiple subjects
        for subject in subjects:
            preprints = fetch_preprints_metadata(subject)
            metadata_list = process_preprints(preprints, subject)
            csv_name = subject.replace(' ', '_').lower()
            df = pd.DataFrame(metadata_list)
            df.to_csv(f"{csv_name}.csv", index=False)
            print(f"Saved {len(metadata_list)} preprints for {subject}")

if __name__ == "__main__":
    # Example usage
    STUDY1_DIR = Path(__file__).parent.parent
    
    # Define a common parent directory for all downloaded articles
    ARTICLES_PARENT_DIR = STUDY1_DIR / "articles"
    
    # Define specific, absolute paths for each source
    ARXIV_DOWNLOAD_DIR = ARTICLES_PARENT_DIR / "arxiv_downloads"
    OSF_DOWNLOAD_DIR = ARTICLES_PARENT_DIR / "osf_downloads"

    subjects = [
    "Engineering",
    "Social and Behavioral Sciences",
    "Business",
    "Life Sciences"
    ] # You can add more subjects as needed, list available on the osf.io website.

    # Create an article downloader instance
    downloader = ArticleDownloader()

    # Download articles from arXiv                
    downloader.arxiv_download(
    name="Your Name",
    email="youremailaddress@example.com",
    download_dir=ARXIV_DOWNLOAD_DIR,
    max_results=1,
    )

    # Download articles from OSF
    downloader.osf_download(
        subjects=subjects,
        download_dir=OSF_DOWNLOAD_DIR,
        max_results=1)

    ### --- This is how it got used for the experiment --- ###
    # subjects = [
    # "Engineering",
    # "Social and Behavioral Sciences",
    # "Business",
    # "Life Sciences"
    # ]

    # # Create an article downloader instance
    # downloader = ArticleDownloader()

    # # Download articles from arXiv                
    # downloader.arxiv_download(
    # name="Your Name",
    # email="youremailaddress@example.com",
    # max_results=25,
    # )

    # # Download articles from OSF
    # downloader.osf_download(subjects=subjects, max_results=200)