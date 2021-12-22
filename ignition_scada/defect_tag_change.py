"""To record that foam has gone out of spec and when it comes back in how much was out."""

import json

from Shared.ptag import Ptag

print('mahlo popup signal - client scope development')

if not initialChange:

	# don't run on other dataexport projects
	dev_system = system.net.getHostName() == u'MCGLAUGHLINLT10'
	if dev_system:
		# these will be used either going out or coming in
		lam_num = 1  # TODO: set this from the event source tagpath
		def_id = Ptag(
			'[default]Miscellaneous Tags/Testing only tags/mahlo_popup/current_defect_id')  # todo each lam should
		# have its own
		test_host_ip = 'http://localhost:5000'
		defects_url = test_host_ip + '/defect'

		# the thickness has gone out of spec
		if newValue.getValue():
			from pprint import pprint
			from Shared.ptag import Ptag

			# dictionary of {'database_column': {1: 'tag_path/for_lam1/value', 2: 'tag_path/for_lam2/value'}}
			current_data_dict = {
				'source_lot_number': {1: '[default]MAHLO/LAM1/BatchID', 2: '[default]MAHLO/LAM2/BatchID'},
				'mahlo_length': {1: '[default]MAHLO/LAM1/MdMeterCount', 2: '[default]MAHLO/LAM2/MdMeterCount'}}
			# TODO: length at start, recipe, what else?

			# iterate, getting the current value for this laminator's mahlo tags
			for column, tag_path in current_data_dict.iteritems():
				current_data_dict[column] = Ptag(tag_path[lam_num]).val

			current_data_dict['defect_type'] = 'thickness'
			pprint(current_data_dict)

			# record json is coming back with a bunch of nulls; successfully created though
			result = json.loads(system.net.httpPost(defects_url, current_data_dict))
			print('new_def result:', result)
			def_id.val = result['id']

		# the thickness has gone back in spec
		else:
			# check if there is a current defect (this being None now SHOULDN'T be possible, and seems like the kind
			# of thing
			# that somehow would anyway)
			if def_id.val:
				# need the initial length either from a get or stored in a tag etc.
				#			db_dict = system.net.httpget(defects_url, {'id': def_id.val})
				db_dict = {}  # we only need the updated values for put
				db_dict['defect_end_ts'] = system.date.now()
				print('updating defect_end_ts to {}'.format(db_dict['defect_end_ts']))

				result = system.net.httpPut(defects_url, db_dict)
				print('update result: {}'.format(result))
				# reset this to no current defect
				def_id.val = None
			else:
				print('No def_id.val; record this somewhere so we can see what happened at his time.')
