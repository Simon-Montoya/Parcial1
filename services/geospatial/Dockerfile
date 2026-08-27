FROM public.ecr.aws/lambda/python:3.12 AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    --target /build/python \
    -r requirements.txt

FROM public.ecr.aws/lambda/python:3.12

COPY --from=builder /build/python ${LAMBDA_TASK_ROOT}
COPY app ${LAMBDA_TASK_ROOT}/app

CMD ["app.main.handler"]