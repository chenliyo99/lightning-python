from lightning import Lightning
from functools import wraps
import inspect


def viztype(VizType):

    # wrapper that passes inputs to cleaning function and creates viz
    @wraps(VizType.clean)
    def plotter(self, *args, **kwargs):
        if not hasattr(self, 'session'):
            self.create_session()
        if True and kwargs['height'] is None and kwargs['width'] is None:
            if self.size != 'full':
                kwargs['width'] = SIZES[self.size]

        viz = VizType.baseplot(self.session, VizType._name, *args, **kwargs)
        self.session.visualizations.append(viz)
        return viz

    # get desired function name if different than plot type
    if hasattr(VizType, '_func'):
        func = VizType._func
    else:
        func = VizType._name

    # crazy hack to give the dynamically generated function the correct signature
    # based on: http://emptysqua.re/blog/copying-a-python-functions-signature/
    # NOTE currently only handles functions with keyword arguments with defaults of None

    options = {}
    if hasattr(VizType, '_options'):
        options = VizType._options

    formatted_options = ', '.join(['%s=%s' % (key, value.get('default_value')) for (key, value) in options.items()])
    argspec = inspect.getargspec(VizType.clean)
    formatted_args = inspect.formatargspec(*argspec)
    fndef = 'lambda self, %s, %s: plotter(self,%s, %s)' \
            % (formatted_args.lstrip('(').rstrip(')'),
               formatted_options, formatted_args[1:].replace('=None', '').rstrip(')'),
               ', '.join('%s=%s' % (key, key) for key in options.keys()))

    fake_fn = eval(fndef, {'plotter': plotter})
    plotter = wraps(VizType.clean)(fake_fn)

    # manually assign a plot-specific name (instead of 'clean')
    plotter.__name__ = func

    # add plotter to class
    setattr(Lightning, func, plotter)

    return VizType

SIZES = {
    'small': 400,
    'medium': 600,
    'large': 800,
}
