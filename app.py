from flask import Flask, render_template
import fhirclient.models.patient as p
import fhirclient.models.observation as o
import fhirclient.models.sequence as s
from fhirclient import client
import json
import re

# create the application object
APP = Flask(__name__, static_folder='static')
settings = {
    'app_id': 'my_web_app',
    'api_base': 'http://snapp.clinfhir.com:8081/baseDstu3/'
}
#Initialize a global smart token to use as the server
smart = client.FHIRClient(settings=settings)
#The ID for the patient we wish to extract FHIR resources for
patID = 'Patient/cf-1521035411812'

def htt_test(fa):
    #Find all repeat stretches
    repeats = re.search('(CAG)+', fa.upper())
    inter = False
    red = False
    pos = False
    #Examine the length of each stretch, testRanges*3 because repeats are not decoupled
    for r in repeats.group():
        if len(r) > 78 and len(r) <= 105:
            inter = True
        elif len(r) > 105 and len(r) <= 117:
            red = True
        elif len(r) > 117:
            pos = True
    #Return test result 
    if pos:
        return "POSITIVE"
    elif red:
        return "POSITIVE (REDUCED PENETRANCE)"
    elif inter:
        return "INTERMEDIATE"
    else:
        return "NEGATIVE"

def getPatient():
    """
        Extract basic demographic information from the Patient FHIR resource
    """
    pID = patID.split('/')[1]
    patient = p.Patient.read(pID, smart.server).as_json()
    return 'Name: ' + patient['name'][0]['text'] + '</br>Gender: ' + patient['gender'] + '</br>DOB: ' + patient['birthDate'] 

def getObservations():
    """
        Extract data from the Observation FHIR resource
    """
    search = o.Observation.where(struct={'subject': patID})
    observations = search.perform_resources(smart.server)
    for obs in observations:
        o_out = obs.as_json()
    return 'Reason for visit: ' + o_out['code']['coding'][0]['display']

@APP.route('/results')
def getSequence():
    """
        Extract a fasta file from the Sequence FHIR resource
    """
    search = s.Sequence.where(struct={'patient': patID})
    sequences = search.perform_resources(smart.server)
    for seq in sequences:
        s_out = htt_test(seq.as_json()['observedSeq'])
    p_out = getPatient()
    o_out = getObservations()
    
    return render_template('index.html', pat=p_out, obs=o_out, seq=s_out)
    

@APP.route('/')
def home():
    """
        Landing page for the app, displays patient and observation data by default
    """
    p_out = getPatient()
    o_out = getObservations()    
    return render_template('index.html', pat=p_out, obs=o_out)

# start the server with the 'run()' method
if __name__ == '__main__':
    APP.run(debug=True, host="0.0.0.0", port=8000)
