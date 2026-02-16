import asyncio
import base64
import json
import re
from base64 import b64decode
import aiohttp
import cloudscraper
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from logger import LOGGER

# Hardcoded keys from ApnaEx/appex_v4.py
AES_KEY = b'638udh3829162018'
AES_IV = b'fedcba9876543210'

def decrypt(enc):
    """Decrypts AES-encrypted strings from Appx API."""
    try:
        if not enc:
            return ""
        enc = b64decode(enc.split(':')[0])
        if len(enc) == 0:
            return ""
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        plaintext = unpad(cipher.decrypt(enc), AES.block_size)
        return plaintext.decode('utf-8')
    except Exception as e:
        LOGGER.error(f"Decryption error: {e}")
        return ""

def decode_base64(encoded_str):
    try:
        decoded_bytes = base64.b64decode(encoded_str)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return str(e)

async def fetch(session, url, headers):
    """Async fetch helper."""
    try:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                LOGGER.error(f"Error fetching {url}: {response.status}")
                return {}
            content = await response.text()
            # Some responses might be HTML wrapped JSON, handled via soup
            try:
                soup = BeautifulSoup(content, 'html.parser')
                return json.loads(str(soup))
            except:
                return json.loads(content)
    except Exception as e:
        LOGGER.error(f"Fetch error {url}: {e}")
        return {}

async def process_video(session, api_base, course_id, subject_id, subject_name, topic_id, topic_name, video, headers):
    """Process a single video item and return formatted dict."""
    video_id = video.get("id")
    video_title = video.get("Title", "Unknown Video")
    
    extracted_items = []
    
    try:
        details_url = f"{api_base}/get/fetchVideoDetailsById?course_id={course_id}&video_id={video_id}&ytflag=0&folder_wise_course=0"
        r4 = await fetch(session, details_url, headers)
        
        if not r4 or not r4.get("data"):
            return []

        data = r4.get("data", {})
        vt = data.get("Title", video_title)
        
        # 1. Main Video Link
        fl = data.get("video_id", "")
        if fl:
            dfl = decrypt(fl)
            final_link = f"https://youtu.be/{dfl}"
            extracted_items.append({
                "name": vt,
                "url": final_link,
                "type": "video",
                "topicName": topic_name,
                "subjectName": subject_name
            })

        # 2. Download Link (often actual video file)
        vl = data.get("download_link", "")
        if vl:
            dvl = decrypt(vl)
            if ".pdf" not in dvl:
                extracted_items.append({
                    "name": vt,
                    "url": dvl,
                    "type": "video",
                    "topicName": topic_name,
                    "subjectName": subject_name
                })

        # 3. Encrypted Links (HLS/Dash usually)
        encrypted_links = data.get("encrypted_links", [])
        if encrypted_links:
            # Prioritize first link or specific quality logic if needed
            first_link = encrypted_links[0]
            path = first_link.get("path")
            key = first_link.get("key")
            
            if path:
                decrypted_path = decrypt(path)
                final_url = decrypted_path
                # If key exists, it might be clear key or needs embedding. 
                # Autoappx schema mostly takes 'url' string. 
                # If key is needed for playback, typically it's embedded or handled by player.
                # appex_v4 formats it as "url*key". Autoappx might need adaptation for this.
                # For now, we'll store url. If key is present, we might append it or handle based on Autoappx player support.
                if key:
                   decrypted_key = decode_base64(decrypt(key))
                   # If Autoappx supports headers/keys in URL field or separate field?
                   # Standard appxdata just returns 'url'. 
                   # We will follow appex_v4 format: url*key if key exists.
                   final_url = f"{decrypted_path}*{decrypted_key}"
                
                extracted_items.append({
                    "name": vt,
                    "url": final_url,
                    "type": "video",
                    "topicName": topic_name,
                    "subjectName": subject_name
                })
        
        # 4. PDF Materials attached to Video
        if "material_type" in data:
            # Check for PDFs in video material
            p1 = data.get("pdf_link", "")
            pk1 = data.get("pdf_encryption_key", "")
            if p1:
                 dp1 = decrypt(p1)
                 # Handle key if needed
                 extracted_items.append({
                    "name": f"{vt} (PDF)",
                    "url": dp1,
                    "type": "pdf",
                    "topicName": topic_name,
                    "subjectName": subject_name
                })

        return extracted_items

    except Exception as e:
        LOGGER.error(f"Error processing video {video_id}: {e}")
        return []

async def handle_course_topic(session, api_base, course_id, subject_id, subject_name, topic, headers):
    """Handle a single topic: fetch videos and process them."""
    topic_id = topic.get("topicid")
    topic_name = topic.get("topic_name")
    
    url = f"{api_base}/get/livecourseclassbycoursesubtopconceptapiv3?courseid={course_id}&subjectid={subject_id}&topicid={topic_id}&conceptid=&start=-1"
    r3 = await fetch(session, url, headers)
    video_data = sorted(r3.get("data", []), key=lambda x: x.get("id"))
    
    tasks = [
        process_video(session, api_base, course_id, subject_id, subject_name, topic_id, topic_name, video, headers)
        for video in video_data
    ]
    results = await asyncio.gather(*tasks)
    
    # Flatten results
    return [item for sublist in results for item in sublist]

async def extract_batch_apnaex_logic(batch_id, api_base, token, userid="-2"):
    """
    Main entry point for ApnaEx extraction logic using asyncio.
    
    Args:
        batch_id (str): The course/batch ID.
        api_base (str): Base API URL (e.g. https://api.classx.co.in).
        token (str): Auth token.
        userid (str): User ID (optional, defaults to -2 if not strictly needed or extracted).
        
    Returns:
        list: List of dictionaries containing extracted content.
    """
    
    headers = {
        "Client-Service": "Appx",
        "source": "website",
        "Auth-Key": "appxapi",
        "Authorization": token,
        "User-ID": userid,
        "User-Agent": "okhttp/4.9.1"
    }
    
    # Ensure protocol
    if not api_base.startswith("http"):
        api_base = f"https://{api_base}"

    all_data = []
    
    async with aiohttp.ClientSession() as session:
        # Fetch Subjects
        subjects_url = f"{api_base}/get/allsubjectfrmlivecourseclass?courseid={batch_id}&start=-1"
        r1 = await fetch(session, subjects_url, headers)
        
        subjects = r1.get("data", [])
        if not subjects:
            LOGGER.warning(f"No subjects found for batch {batch_id}")
            return []
            
        for subject in subjects:
            si = subject.get("subjectid")
            sn = subject.get("subject_name")
            
            # Fetch Topics for Subject
            topics_url = f"{api_base}/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={si}&start=-1"
            r2 = await fetch(session, topics_url, headers)
            topics = sorted(r2.get("data", []), key=lambda x: x.get("topicid"))
            
            # Process Topics concurrently
            topic_tasks = [
                handle_course_topic(session, api_base, batch_id, si, sn, t, headers)
                for t in topics
            ]
            topic_results = await asyncio.gather(*topic_tasks)
            
            # Aggregate data
            for res in topic_results:
                if res:
                    all_data.extend(res)
                    
    return all_data
