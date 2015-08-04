from string import Formatter
from pygments.token import Token
from pygments.style import Style
from pygments.styles.default import DefaultStyle

class ScapStyle(Style):
    styles = DefaultStyle.styles.copy()
    styles.update({
        Token: '#cccccc',
        Token.Text: '#eeeeee',
        Token.Prompt: '#aaaaaa',
        Token.Toolbar: '#9999ff bg:#333333',
        Token.Toolbar.Text: '#999999',
        Token.Toolbar.Value: '#cccc33',
        Token.Name.Variable: "#aaccff",
    })

def get_prompt_tokens(context):
    return tokenize_string("u@{cwd@Prompt} scap> ", context, text_token=Token.Prompt)

def get_toolbar_tokens(context):
    return tokenize_string("cwd: {cwd} | {cmd:Last Command}", context)

def tokenize_string(text, values,
                    text_token=Token.Toolbar.Text,
                    value_token=Token.Toolbar.Value):
    fmt = Formatter()
    tokens = []
    parsed = fmt.parse(text)
    for x in parsed:
        part,key,lbl,_ = x
        #print x
        try:
            if len(part):
                # static text that appears before the dynamic value:
                tokens.append((text_token, part))

            if '@' in key:
                # @Style in the format string overrides the style token used
                # for this ui element
                key, _, style = key.partition('@')
                vt = getattr(Token, style)
            else:
                # use default (or caller-provided) style token
                vt = value_token

            # look up the dynamic value:
            val = str(values[key])
            if (len(val)):
                # if there is a label, display it first
                if (len(lbl)):
                    tokens.append((text_token, str(lbl)+": "))
                # finally display the dynamic value
                tokens.append((vt, val))
        except:
            continue
    return tokens