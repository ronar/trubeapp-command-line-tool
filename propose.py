#!/usr/local/bin/python

import os
import sys
import requests
import json
import argparse
import pickle

apiURL = 'http://api.dev.trubeapp.com/v3'
user = ''
password = ''
partner = {'id': '', 'token': '', 'email': ''}

messages = {
    'wipe': 'wipe all partner auth info',
    'verbosity': 'increase output verbosity',
    'list_bookings': 'prints list of bookings',
    'proposal': {
        'help'   : 'partner proposes for booking',
        'request': 'trying to propose for the booking..',
        'success': 'booking ({}) was successfull',
        'failure': 'there was error while proposing booking: '
    },
    'start_session': {
        'help'   : 'partner starts a session',
        'request': 'trying to start the session..',
        'success': 'booking ({}) was started successfully',
        'failure': 'there was error while starting the session: '
    },
    'conclude_session': {
        'help'   : 'partner concludes a session',
        'request': 'trying to conclude a session..',
        'success': 'booking ({}) was stopped successfully',
        'failure': 'there was error while stopping the session: '
    },
    'decline_session': {
        'help'   : 'partner declines a booking',
        'request': 'trying to decline the booking..',
        'success': 'booking ({}) was declined successfully',
        'failure': 'there was error while declining the session: '
    },
    'reject': {
        'help'   : 'partner rejects an assigned session',
        'request': 'trying to reject the session..',
        'success': 'booking ({}) was rejected successfully',
        'failure': 'there was error while rejecting the session: '
    }
}

parser = argparse.ArgumentParser('TruBe API command line tool')
parser.add_argument('-w', '--wipe', action='store_true', help=messages['wipe'])
parser.add_argument('-v', '--verbose', action='store_true', help=messages['verbosity'])
parser.add_argument('-u', '--user', type=str, action='store', default=user)
parser.add_argument('--password', type=str, action='store', default=password)
parser.add_argument('-l', '--list-bookings', action='store_true', help=messages['list_bookings'])
group = parser.add_mutually_exclusive_group()
group.add_argument('-p', '--propose', type=int, action='store', help=messages['proposal']['help'])
group.add_argument('-s', '--start-session', type=int, action='store', help=messages['start_session']['help'])
group.add_argument('-c', '--conclude-session', type=int, action='store', help=messages['conclude_session']['help'])
group.add_argument('-d', '--decline-session', type=int, action='store', help=messages['decline_session']['help'])
group.add_argument('-r', '--reject', type=int, action='store', help=messages['reject']['help'])
args = parser.parse_args()

# wipe the token
if args.wipe:
    if args.verbose:
        print 'wiping the partner..'

    try:
        os.remove('partner.pickle')
    except Exception as e:
        print 'could not wipe the partner data..'
    else:
        if args.verbose:
            print 'wiping done..'


def retrievePartner():
    try:
        with open('partner.pickle', 'rb') as handle:
            partner = pickle.load(handle)

        if args.verbose:
            print 'got cached partner: ', partner

        return partner
    except IOError as e:
        print 'no cached partner were found'


def cachePartner(data):
    with open('partner.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        if args.verbose:
            print 'partner data has been successfully cached'


def getHeaders():
    return {'Content-Type': 'application/json;charset=utf-8'}


def auth():
    tokenId = ''
    partnerId = ''

    partner = retrievePartner()

    if partner is not None and partner['email'] == args.user:
        return

    try:
        payload = {'email': args.user, 'password': args.password}
        response = requests.post(apiURL + '/partners/auth', headers=getHeaders(), data=json.dumps(payload))
    except Exception as e:
        print 'there was error while authenticating: ', e
    else:
        if response.status_code != 200:
            print response.raise_for_status()
            # sys.exit('na. probably your auth info was crap. exting..')
        else:
            resp = response.json()
            if 'authToken' in resp:
                if 'id' in resp:
                    tokenId = resp['authToken']['id']
                    # saveToken(token)

            if 'id' in resp:
                partnerId = resp['id']
                # savePartnerId(partnerId)

                if args.verbose:
                    print 'got partner: ' + resp['firstName'] + ' ' + resp['familyName']

            if tokenId and partnerId:
                partner = {'id': partnerId, 'tokenId': tokenId, 'email': resp['email']}
                cachePartner(partner)



def withAuthInfo(func):
    def funcWrapper(url, headers = {}, payload = {}):
        tokenId = ''
        partnerId = ''

        partner = retrievePartner()

        print 'Making request'

        if partner is not None and partner['email'] == args.user:
            headers.update({'AUTH_TOKEN': partner['tokenId']})
            url = apiURL + '/partners/{}/{}'.format(partner['id'], url)

            return func(url, headers, payload)

        try:
            authPayload = {'email': args.user, 'password': args.password}
            response = requests.post(apiURL + '/partners/auth', headers=getHeaders(), data=json.dumps(authPayload))
        except Exception as e:
            print 'there was error while authenticating: ', e
        else:
            if response.status_code != 200:
                print response.raise_for_status()
                # sys.exit('na. probably your auth info was crap. exting..')
            else:
                resp = response.json()
                if 'authToken' in resp:
                    if 'id' in resp:
                        tokenId = resp['authToken']['id']
                        # saveToken(token)

                if 'id' in resp:
                    partnerId = resp['id']
                    # savePartnerId(partnerId)

                    if args.verbose:
                        print 'got partner: ' + resp['firstName'] + ' ' + resp['familyName']

                if tokenId and partnerId:
                    partner = {'id': partnerId, 'tokenId': tokenId, 'email': resp['email']}
                    cachePartner(partner)

                headers.update({'AUTH_TOKEN': tokenId})
                url = apiURL + '/partners/{}/{}'.format(partnerId, url)

                return func(url, headers, payload)

    return funcWrapper


def bookingsPath(bookingId, path):
    return 'bookings/{}/{}'.format(bookingId, path)


def mapBookings(val):
    print val
    return val


def dumpResponse(response):
    if response.status_code != 200:
        print response.raise_for_status()
    elif args.verbose:
        resp = response.json()

        if args.verbose:
            print 'response:'
            print json.dumps(resp, indent=4, sort_keys=True)


# Make kwargs
@withAuthInfo
def makeRequest(url, headers = {}, payload = {}):
    print json.dumps(payload, indent=4, sort_keys=True)
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    dumpResponse(response)


def requestFnFactory(path, messages):
    def func(bookingId, payload = {}):
        try:
            if args.verbose:
                print messages['request']

            makeRequest(bookingsPath(bookingId, path), getHeaders(), payload)
        except Exception as e:
            print messages['failure'], e
        else:
            # if args.verbose:
            print messages['success'].format(bookingId)


    return func


partnerProposals = requestFnFactory('acceptance', messages['proposal'])
partnerStartsSession = requestFnFactory('session-start', messages['start_session'])
partnerStopsSession = requestFnFactory('session-stop', messages['conclude_session'])
partnerDeclinesSession = requestFnFactory('session-declined', messages['decline_session'])
partnerRejectsSession = requestFnFactory('cancellation', messages['reject'])


@withAuthInfo
def getPartnerBookings(path, headers = {}, payload = {}):
    try:
        if args.verbose:
            print 'trying to fetch the bookings..'

        headers.update(getHeaders())
        response = requests.get(path, headers=headers)
    except Exception as e:
        print 'there was error: ', e
    else:
        if response.status_code != 200:
            print response.raise_for_status()
        else:
            resp = response.json()

            if args.verbose:
                print 'response:'
                print json.dumps(resp, indent=4, sort_keys=True)

            if 'content' in resp:
                if len(resp['content']) > 0:
                    bookings = [v['id'] for v in resp['content']]

                    print 'id of bookings:'
                    print bookings
                else:
                    print 'no content!'


if args.list_bookings:
    getPartnerBookings('pending-bookings')


if args.propose:
    #payload = {'expiration': 10, 'offsets': [{'time': 10, 'surcharge': 10.05, 'venueFee': 10.05}, {'time': 20, 'surcharge': 10.05, 'venueFee': 10.05}, {'time': 30, 'surcharge': 10.05, 'venueFee': 10.05}, {'time': 40, 'surcharge': 10.05, 'venueFee': 10.05}, {'time': 50, 'surcharge': 10.05, 'venueFee': 10.05}, {'time': 60, 'surcharge': 10.05, 'venueFee': 10.05}]}
    payload = {'offsets': [10, 20, 30, 40, 50, 60]}
    partnerProposals(args.propose, payload)


if args.start_session:
    partnerStartsSession(args.start_session)


if args.conclude_session:
    partnerStopsSession(args.conclude_session)


if args.decline_session:
    payload = {'reason': 'Restricted by travel or distance'}
    partnerDeclinesSession(args.decline_session, payload)


if args.reject:
    partnerRejectsSession(args.reject)
