from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.observation as o
import json

settings = {
    'app_id': 'my_web_app',
    'api_base': 'http://fhirtest.uhn.ca/baseDstu3/'
}

def query():
    fhirServer = client.FHIRClient(settings=settings).server

    #Will print the first names of all males in the server
    search = p.Patient.where(struct={'gender':'male'})
    results = search.perform_resources(fhirServer)
    for r in results:
        print(r.as_json()['name'][0]['given'][0])

    #Will print patient ID's for all patients with a recorded systolic BP
    search = o.Observation.where(struct={'code-value-concept':'8480-6'})
    results = search.perform_resources(fhirServer)
    for r in results:
        print(r.as_json()['subject']['reference'])

if __name__=="__main__":
    query()
