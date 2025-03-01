from grist_api import GristDocAPI
import os

SERVER = "https://grist.insomniafest.ru"
DOC_ID = "mhwDM83vLmT3HsFa4CJsTh"
GRIST_API_KEY = "15ef01f2503ecc4f9201a0841e6d70beb2338456"
#GRIST_API_KEY = "def9b5d12833fe4fd45efe30a2d6d0c263c8eb0a"

os.environ["GRIST_API_KEY"] = GRIST_API_KEY

api = GristDocAPI(DOC_ID, server=SERVER)


#people = api.fetch_table("People")[0]
#print(people)

#directions = api.fetch_table("Directions2025")[0]
#print(directions)

#participations = api.fetch_table("Participations")[0]
#print(participations)

#participation_statuses = api.fetch_table("Participation_statuses")[0]
#print(participation_statuses)

participant = api.fetch_table("Participations", filters={"person":0})[0]
print(participant)

'''
directions = api.fetch_table("Directions2025")[0]
print(directions)

locations = api.fetch_table("Locations2025")[0]
print(locations)

participations = api.fetch_table("Participations")[0]
print(participations)
print(participations.person_id)
participant = api.fetch_table("People", filters={"id":participations.person})[0]
print(participant)
team = api.fetch_table("Teams", filters={"id":participations.team})[0]
print(team)
status = api.fetch_table("Participation_statuses", filters={"id":participations.status})[0]
print(status)

teams = api.fetch_table("Teams")[0]
print(teams)
'''



