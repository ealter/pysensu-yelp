import pysensu_yelp
import mock
import contextlib
import json
import socket
import pytest

class TestPySensuYelp:

    test_name = 'then_i_saw_her_face'
    test_runbook = 'now_im_a_believer'
    test_status = 0
    test_output = 'without_a_trace'
    test_team = 'no_doubt_in_my_mind'
    test_page = False
    test_tip = 'but_who_docks_the_docker'
    test_check_every = '1M'
    test_realert_every = 99
    test_alert_after = '1Y'
    test_irc_channels = ['#sensu_test']


    event_dict = {
        'name': test_name,
        'status': test_status,
        'output': test_output,
        'handler': 'default',
        'team': test_team,
        'runbook': test_runbook,
        'tip': test_tip,
        'interval': pysensu_yelp.human_to_seconds(test_check_every),
        'page': test_page,
        'realert_every': test_realert_every,
        'alert_after': pysensu_yelp.human_to_seconds(test_alert_after),
        'irc_channels': test_irc_channels,
    }
    event_hash = json.dumps(event_dict)

    check_dict = {
        'name': test_name,
        'runbook': test_runbook,
        'team': test_team,
        'page': test_page,
        'tip': test_tip,
        'check_every': test_check_every,
        'realert_every': test_realert_every,
        'alert_after': test_alert_after,
        'irc_channels': test_irc_channels,
    }

    def test_human_to_seconds(self):
        assert pysensu_yelp.human_to_seconds('1s') == 1
        assert pysensu_yelp.human_to_seconds('1m1s') == 61
        assert pysensu_yelp.human_to_seconds('1M1m') == 2592060
        assert pysensu_yelp.human_to_seconds('1Y1M1W1D1h1m1s') == 34822861

    def test_send_event_valid_args(self):
        magic_skt = mock.MagicMock()
        with mock.patch('socket.socket', return_value=magic_skt) as skt_patch:
            pysensu_yelp.send_event(self.test_name, self.test_runbook,
                                    self.test_status, self.test_output,
                                    team=self.test_team, page=self.test_page, tip=self.test_tip,
                                    check_every=self.test_check_every,
                                    realert_every=self.test_realert_every,
                                    alert_after=self.test_alert_after,
                                    irc_channels=self.test_irc_channels)
            skt_patch.assert_called_once()
            magic_skt.connect.assert_called_once_with(pysensu_yelp.SENSU_ON_LOCALHOST)
            magic_skt.sendall.assert_called_once_with(self.event_hash + '\n')
            magic_skt.close.assert_called_once()

    def test_send_event_bad_status(self):
        magic_skt = mock.MagicMock()
        with mock.patch('socket.socket', return_value=magic_skt) as skt_patch:
            with pytest.raises(ValueError):
                pysensu_yelp.send_event(self.test_name, self.test_runbook,
                                        91913591, self.test_output,
                                        team=self.test_team, page=self.test_page, tip=self.test_tip,
                                        check_every=self.test_check_every,
                                        realert_every=self.test_realert_every,
                                        alert_after=self.test_alert_after,
                                        irc_channels=self.test_irc_channels)
            skt_patch.assert_not_called()

    def test_send_event_no_runbook(self):
        magic_skt = mock.MagicMock()
        with mock.patch('socket.socket', return_value=magic_skt) as skt_patch:
            with pytest.raises(ValueError):
                pysensu_yelp.send_event(self.test_name, '',
                                        self.test_status, self.test_output,
                                        team=self.test_team, page=self.test_page, tip=self.test_tip,
                                        check_every=self.test_check_every,
                                        realert_every=self.test_realert_every,
                                        alert_after=self.test_alert_after,
                                        irc_channels=self.test_irc_channels)
            skt_patch.assert_not_called()

    def test_send_event_from_check(self):
        with mock.patch('pysensu_yelp.send_event', return_value=True) as send_patch:
            pysensu_yelp.send_event_from_check(self.check_dict, self.test_status, self.test_output)
            send_patch.assert_called_once_with(self.test_name, self.test_runbook,
                                               self.test_status, self.test_output,
                                               team=self.test_team, page=self.test_page,
                                               tip=self.test_tip, check_every=self.test_check_every,
                                               realert_every=self.test_realert_every,
                                               alert_after=self.test_alert_after,
                                               irc_channels=self.test_irc_channels)

    def test_SensuEventEmitter(self):
        test_emitter = pysensu_yelp.SensuEventEmitter(self.test_name, self.test_runbook,
                                                      team=self.test_team,
                                                      page=self.test_page,
                                                      tip=self.test_tip,
                                                      check_every=self.test_check_every,
                                                      realert_every=self.test_realert_every,
                                                      alert_after=self.test_alert_after,
                                                      irc_channels=self.test_irc_channels)
        with mock.patch('pysensu_yelp.send_event', return_value=True) as send_patch:
            test_emitter.emit_event(self.test_status, self.test_output)
            send_patch.assert_called_once_with(self.test_name, self.test_runbook,
                                               self.test_status, self.test_output,
                                               team=self.test_team, page=self.test_page,
                                               tip=self.test_tip, check_every=self.test_check_every,
                                               realert_every=self.test_realert_every,
                                               alert_after=self.test_alert_after,
                                               irc_channels=self.test_irc_channels)