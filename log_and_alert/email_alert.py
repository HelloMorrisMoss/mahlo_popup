import logging
import smtplib
import traceback
from email.mime.text import MIMEText

lg = logging.getLogger('mahlo_pdf_parser')


def send_email(recipient_list: list, subject: str, body: str, sender: str, smtp_ip: str):
    """Sends an email using a smtp relay.

    Example:
        send_email(["name@address.com"], "Did you get this email?", "Hello, let me know if you don't get this email.")


    for editing, example
        send_to = ['brian.lifeof@mail.com', 'blue.fjords@spam.com']
        subj = 'this is an email subject'
        body = 'this is the body of the email, it has some words'
        send_email(send_to, subj, body)

        This is only able to handle simple text emails. Attachments are not implemented.
        """
    from datetime import datetime
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipient_list) if len(recipient_list) > 1 else recipient_list[0]

    try:
        smtp_obj = smtplib.SMTP(smtp_ip)
        smtp_obj.sendmail(sender, recipient_list, msg.as_string())
    except smtplib.SMTPException:
        lg.error('%s - error: %s', datetime.now(), traceback.format_exc())
        smtp_obj.close()
    except TimeoutError:
        lg.error('%s - ip: %s error: %s', datetime.now(), smtp_ip, traceback.format_exc())
    except OSError:
        lg.error('%s - error: %s', datetime.now(), traceback.format_exc())


def set_up_alert(cfg_dict, subject: str = '', body: str = ''):
    """Use values based on config file settings and pass on to send_email fn.

    :param cfg_dict: dictionary
        contains the settings for sending emails.
    :param subject: string
        The subject line for the email.
    :param body: string
        The body message for the email.
    """
    recipients = [cfg_dict['email_settings']['recipient_list']]
    sender = cfg_dict['email_settings']['sender_name']
    smtp_ip = cfg_dict['email_settings']['smtp_server']
    body = body  # cfg_dict['email settings'][body] if not body else body
    subj = 'Automatic message.' if not subject else subject
    send_email(recipient_list=recipients, subject=subj, body=body, sender=sender, smtp_ip=smtp_ip)


def get_email_cfg_dict(lam_num: int = None):
    """Get the dictionary of settings used by set_up_alert

    :param lam_num: int, the laminator number
    :return: dict
    """
    from untracked_config.email_cfg_dict import email_cfg_dict

    if lam_num is not None:
        f_sender = email_cfg_dict['email_settings']['sender_name'].format(num=lam_num)
        email_cfg_dict['email_settings']['sender_name'] = f_sender
    return email_cfg_dict


if __name__ == '__main__':
    # from config_parsing import get_config
    from datetime import datetime

    lg.debug('beginning email test')
    # where to find the config file

    # the dictionary of config settings
    # config_dic = get_config(config_path)
    config_dic = get_email_cfg_dict(0)
    set_up_alert(config_dic, 'test email', 'this is a test email {}'.format(datetime.now()))
    lg.debug('finishing email test')
