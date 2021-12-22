test_host_ip = 'http://localhost:5000'
defects_url = test_host_ip + '/popup'
hc = system.net.httpClient()

# if newValue.getValue():
action_dict = {'action': 'shrink' if newValue.getValue() else 'show'}

result = hc.post(defects_url, params=action_dict)

print('popup for mahlo start result: {}'.format(result))
