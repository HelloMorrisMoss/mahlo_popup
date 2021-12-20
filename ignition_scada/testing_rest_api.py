"""For use with Ignition SCADA by Inductive automation.

These are rough test scripts built in the designer's script console.
"""
import json
import time

# test_host_ip = 'http://10.155.1.59'  # this won't work either due to the proxy or one of the (how many?) firewalls
test_host_ip = 'http://localhost:5000'

# get the list of defects
get_defects_url = test_host_ip + '/defects'
defects_result = json.loads(system.net.httpGet(get_defects_url))
# print('number of defects in database: {count}'.format(count=len(defects_result)))
# pprint(defects_result)


# get_defect_by_id_headers = {"defect_id": 8}
get_defect_by_id_url = test_host_ip + '/defect'

system.net.httpGet(get_defect_by_id_url, headerValues=get_defect_by_id_headers, usesCache=False)

# show the popup
post_popup_url = test_host_ip + '/popup'

show_popup_data = {"action": "show"}

show_popup_result = system.net.httpPost(post_popup_url, show_popup_data)
print(show_popup_result)
assert ('Showing popup window.' in show_popup_result)

time.sleep(1)

# shrink the popup
show_popup_data = {"action": "shrink"}

shrink_result = system.net.httpPost(post_popup_url, show_popup_data)
assert ('Shrinking popup window' in shrink_result)

# create new defect record
new_defect_record_data = {
 "source_lot_number": 123456,
 "tabcode": "T12345",
 "recipe": 99999,
 "lam_num": 0,
 "defect_type": "thickness",
 "record_creation_source": "ignition_test"
 }

# record json is coming back with a bunch of nulls; successfully created though
system.net.httpPost(get_defect_by_id_url, new_defect_record_data)
