#!/usr/local/bin/python

import os
import sys
import requests
import json
import argparse
import pickle

apiURL = 'http://api.dev.trubeapp.com/v3'
user = 'default@mail.ru'
password = 'default'
partner = {'id': '', 'token': '', 'email': ''}

parser = argparse.ArgumentParser('TruBe API command line tool')
parser.add_argument('-w', '--wipe', action='store_true', help='wipe all partner auth info')
parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
parser.add_argument('-u', '--user', type=str, action='store', default=user)
parser.add_argument('--password', type=str, action='store', default=password)
parser.add_argument('-l', '--list-bookings', action='store_true', help='prints list of bookings')
group = parser.add_mutually_exclusive_group()
group.add_argument('-p', '--propose', type=int, action='store', help='partner proposes for booking')
group.add_argument('-s', '--start-session', type=int, action='store', help='partner starts a session')
group.add_argument('-c', '--conclude-session', type=int, action='store', help='partner concludes a session')
group.add_argument('-d', '--decline-session', type=int, action='store', help='partner declines a booking')
group.add_argument('-t', '--trainer-declining', type=int, action='store', help='partner declines a direct booking')
group.add_argument('-r', '--reject', type=int, action='store', help='partner rejects an assigned session')
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

                headers.update({'AUTH_TOKEN': tokenId})
                url = apiURL + '/partners/{}/{}'.format(partnerId, url)

                print 'headers ', headers
                print 'url ', url

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
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    dumpResponse(response)


def partnerProposal(bookingId):
    payload = {'expiration': 10, 'offsets': [{'time': 10, 'surcharge': 10.05, 'venueFee': 10.05}, {'time': 20, 'surcharge': 10.05, 'venueFee': 10.05}, {'time': 30, 'surcharge': 10.05, 'venueFee': 10.05}, {'time': 40, 'surcharge': 10.05, 'venueFee': 10.05}, {'time': 50, 'surcharge': 10.05, 'venueFee': 10.05}, {'time': 60, 'surcharge': 10.05, 'venueFee': 10.05}]}

    try:
        if args.verbose:
            print 'trying to propose for the booking..'

        makeRequest(bookingsPath(bookingId, 'acceptance'), getHeaders(), payload)
    except Exception as e:
        print 'there was error while proposing booking: ', e
    else:
        # if args.verbose:
        print 'booking ({}) was successfull'.format(bookingId)


def partnerStartsSession(bookingId):
    try:
        if args.verbose:
            print 'trying to start a session..'

        makeRequest(bookingsPath(bookingId, 'session-start'), getHeaders())
    except Exception as e:
        print 'there was error while proposing booking: ', e
    else:
        # if args.verbose:
        print 'booking ({}) was started successfully'.format(bookingId)


def partnerStopsSession(bookingId):
    try:
        if args.verbose:
            print 'trying to conclude a session..'

        makeRequest(bookingsPath(bookingId, 'session-stop'), getHeaders())
    except Exception as e:
        print 'there was error while starting a session: ', e
    else:
        # if args.verbose:
        print 'booking ({}) was stopped successfully'.format(bookingId)


def partnerDeclinesSession(bookingId, reason):
    try:
        if args.verbose:
            print 'trying to propose for the booking..'

        payload = {'reason': reason}

        makeRequest(bookingsPath(bookingId, 'session-declined'), getHeaders(), payload)
    except Exception as e:
        print 'there was error while declining a session: ', e
    else:
        # if args.verbose:
        print 'booking ({}) was declined successfully'.format(bookingId)


def partnerRejectsSession(bookingId):
    try:
        if args.verbose:
            print 'trying to reject the session..'

        makeRequest(bookingsPath(bookingId, 'cancellation'), getHeaders(), payload)
    except Exception as e:
        print 'there was error while rejecting a session: ', e
    else:
        # if args.verbose:
        print 'booking ({}) was rejected successfully'.format(bookingId)


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
    partnerProposal(args.propose)


if args.start_session:
    partnerStartsSession(args.start_session)


if args.conclude_session:
    partnerStopsSession(args.conclude_session)


if args.decline_session:
    partnerDeclinesSession(args.decline_session, 'Restricted by travel or distance')


if args.trainer_declining:
    partnerDeclinesDirectBooking(args.trainer_declining)


if args.reject:
    partnerDeclinesDirectBooking(args.reject)
