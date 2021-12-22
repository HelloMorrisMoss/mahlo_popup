"""To record that foam has gone out of spec and when it comes back in how much was out."""

from Shared.ptag import Ptag

print('mahlo popup signal - client scope development')

if initialChange:
	print('initial subscription: not acting')

else:

	# don't run on other dataexport projects
	dev_system = system.net.getHostName() == u'MCGLAUGHLINLT10'
	if dev_system:
		# these will be used either going out or coming in
		#		lam_num = 1
		lam_num = Shared.L.get_num_from_path(event.getTagPath().toString())
		# todo: each lam should have its own
		def_id = Ptag('[default]Miscellaneous Tags/Testing only tags/mahlo_popup/current_defect_id')
		test_host_ip = 'http://localhost:5000'
		defects_url = test_host_ip + '/defect'
		hc = system.net.httpClient()

		# dictionary of {'database_column': {1: 'tag_path/for_lam1/value', 2: 'tag_path/for_lam2/value'}}
		tagpath_dict = {'source_lot_number': {1: '[default]MAHLO/LAM1/BatchID', 2: '[default]MAHLO/LAM2/BatchID'},
						'mahlo_start_length': {1: '[default]MAHLO/LAM1/MdMeterCount',
											   2: '[default]MAHLO/LAM2/MdMeterCount'},
						'mahlo_end_length': {1: '[default]MAHLO/LAM1/MdMeterCount',
											 2: '[default]MAHLO/LAM2/MdMeterCount'},
						'recipe': {1: '[default]MAHLO/LAM1/KeyName', 2: '[default]MAHLO/LAM2/KeyName'},
						'file_name': {1: '[default]MAHLO/LAM1/FileName', 2: '[default]MAHLO/LAM2/FileName'},
						'tabcode': {1: '[default]MAHLO/LAM1/TiRollCount', 2: '[default]MAHLO/LAM2/TiRollCount'}
						}

		#		# for testing
		#		tagpath_dict = {'source_lot_number': {1: '[default]Miscellaneous Tags/Testing only
		#		tags/mahlo_popup/dummy_mahlo_tags/BatchID'},
		#								'mahlo_start_length': {1: '[default]Miscellaneous Tags/Testing only
		#								tags/mahlo_popup/dummy_mahlo_tags/MdMeterCount'},
		#								'mahlo_end_length': {1: '[default]Miscellaneous Tags/Testing only
		#								tags/mahlo_popup/dummy_mahlo_tags/MdMeterCount'},
		#								'recipe': {1: '[default]Miscellaneous Tags/Testing only
		#								tags/mahlo_popup/dummy_mahlo_tags/KeyName'},
		#								'file_name': {1: '[default]Miscellaneous Tags/Testing only
		#								tags/mahlo_popup/dummy_mahlo_tags/FileName'},
		#								'tabcode': {1: '[default]Miscellaneous Tags/Testing only
		#								tags/mahlo_popup/dummy_mahlo_tags/TiRollCount'}
		#								}

		# the thickness has gone out of spec
		if newValue.getValue():
			from pprint import pprint
			from Shared.ptag import Ptag

			# TODO: length at start, recipe, what else?
			current_data_dict = {}
			# iterate, getting the current value for this laminator's mahlo tags
			for column, tag_path in tagpath_dict.iteritems():
				current_data_dict[column] = Ptag(tag_path[lam_num]).val

			current_data_dict['defect_type'] = 'thickness'
			pprint(current_data_dict)

			# todo: check result code and add retries
			result = hc.post(defects_url, params=current_data_dict).json
			print('new_def result:', result)
			def_id.val = result['id']

		# the thickness has gone back in spec
		else:
			# check if there is a current defect (this being None now SHOULDN'T be possible, and seems like the kind
			# of thing
			# that somehow would anyway)
			if def_id.val:
				# get the values from the database
				result = hc.get(defects_url, params={'id': def_id.val}).json
				print('get current defect result {}'.format(result))

				# we only need the updated values for put
				current_data_dict = {'id': def_id.val, 'defect_end_ts': system.date.now()}
				# the database is on the same system as the gateway, so same time source

				end_length = Ptag(tagpath_dict['mahlo_end_length'][lam_num]).val
				current_data_dict['mahlo_end_length'] = end_length

				current_data_dict['length_of_defect_meters'] = round(end_length - result['mahlo_start_length'], 2)

				print('current_data_dict: {}'.format(current_data_dict))

				# todo: check result code and add retries
				result = hc.put(defects_url, params=current_data_dict).json
				print('update result: {}'.format(result))

				# reset this to no current defect
				def_id.val = None
			else:
				print('No def_id.val; record this somewhere so we can see what happened at his time.')
