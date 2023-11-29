import csv
import os

def get_league_ids():
        league_ids = set()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        tsv_file_path = os.path.join(script_dir, 'leagues_copy.tsv')

        with open(tsv_file_path, 'r', newline='', encoding='utf-8') as tsvfile:
                # Your file processing                 
                # # Use the csv.reader with tab delimiter
                reader = csv.reader(tsvfile, delimiter='\t')

                # Skip the header row
                next(reader)

                # Iterate through rows
                for row in reader:
                        # Assuming the League ID column is in the first position (index 0)
                        league_id = row[0].strip()
                        
                        try:
                                id_int = int(league_id)
                                league_ids.add(id_int)
                        except ValueError:
                                continue;
                
        # Now you have a set with all unique League IDs
        return league_ids
