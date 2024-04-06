import logging

from openbroker import InstrumentsClient
from openbroker.constant import Segment, OptionType
from openbroker.datatype import Instrument

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


contracts = InstrumentsClient()
contracts.update()

contract: Instrument = contracts.find_instrument('NIFTY', Segment.Cash)
print('Cash underlying')
print(contract, end='\n\n')

contract: Instrument = contracts.find_instrument('NIFTY', Segment.Future, '2024-04-25')
print('A future contract')
print(contract, end='\n\n')

contract: Instrument = contracts.find_instrument('NIFTY', Segment.Option,
                                                 '2024-04-25', 21600, OptionType.Call)
print('An option contract')
print(contract, end='\n\n')

print('Saving the contract map to a file (conracts.json)')
contracts.dump('contracts.json')

print('Loading the contract map once again')
new_contract_map = InstrumentsClient()
new_contract_map.load('contracts.json')
print(new_contract_map.find_instrument('NIFTY', Segment.Future, '2024-04-25'))
