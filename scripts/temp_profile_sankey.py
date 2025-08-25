
import sys
# Add project root to path to allow imports
sys.path.append('/home/cgorricho/apps/TAG-Techbridge/TAG-TB-Purpose-Project/2week_poc_execution/hungerhub_poc/')

from src.dashboard.streamlit.enhanced_app import create_real_sankey_diagram
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info("--- Starting Sankey Generation Test ---")
    try:
        # Calling the function directly to test it in isolation
        fig = create_real_sankey_diagram()
        if fig:
            logging.info("--- Sankey Figure Generation FINISHED ---")
        else:
            logging.error("--- Sankey Figure Generation FAILED ---")
    except Exception as e:
        logging.error(f"--- An exception occurred: {e}", exc_info=True)
